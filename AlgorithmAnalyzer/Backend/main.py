import urllib
import os
import json

from flask import request, current_app, send_from_directory
from flask_api import FlaskAPI, status
from flask_cors import CORS

from config import *
from sample_manager.SampleManager import SampleManager, UsernameException

app = FlaskAPI(__name__)
sample_manager = SampleManager(config.SAMPLE_UPLOAD_PATH)

CORS(app)

# TODO: Would be nice to reword endpoints to follow username -> type instead of
#  type -> username for consistency to how currently SampleManager stores them


@app.route("/", methods=['GET'])
def landing_documentation_page():
    """ Landing page for browsable API """

    if request.method == 'GET':
        """ this will list on routes the default endpoint """

        def list_routes():
            """ helper function that returns all routes in a list """
            output = {}
            for rule in app.url_map.iter_rules():
                methods = ', '.join(rule.methods)
                output[urllib.parse.unquote(rule.endpoint)] = {
                    "name": urllib.parse.unquote(rule.endpoint),
                    "description": " ".join(
                        current_app.view_functions[
                            rule.endpoint].__doc__.split()),
                    "methods": urllib.parse.unquote(methods),
                    "url": urllib.parse.unquote(str(request.host_url))[0:-1]
                    + str(rule)
                }

            return output

        return list_routes()


@app.route("/users", methods=['GET'])
def handle_users_endpoint():
    """
    serve list of registered users
    """
    return {'users': sample_manager.get_all_usernames()}, status.HTTP_200_OK


@app.route("/audio/<string:type>", methods=['POST'])
def handling_audio_endpoint(type):
    """
    This handles generic operations that have to do with audio
    being sent/received from test files

    POST to send a new audio file
    """

    if type not in ['train', 'test']:
        return [f"Unexpected type '{type}' requested"], status.HTTP_400_BAD_REQUEST

    if request.method == 'POST':
        if 'file' not in request.files:
            return ['No file part'], status.HTTP_400_BAD_REQUEST
        if 'username' not in request.data:
            return ['No username'], status.HTTP_400_BAD_REQUEST
        app.logger.info(f"add new sample to {type} set")
        username = request.data.get('username')
        file = request.files.get('file')

        try:
            path, recognized_speech = sample_manager.save_new_sample(username, file, type)
        except UsernameException:
            return ['Bad username'], status.HTTP_400_BAD_REQUEST

        return {"username": username,
                "text": f"Uploaded file for {username}, "
                        f"recognized: {recognized_speech}",
                "recognized_speech": str(recognized_speech)
                }, status.HTTP_201_CREATED


@app.route("/audio/<string:type>/<string:username>", methods=['GET'])
def handle_list_samples_for_user(type, username):
    """
    it handles request for listing samples from train or test set
    for particular user

    type: sample set type (train or test)
    username: full name, eg. Hugo Kołątaj or Stanisław
    """
    if type not in ['train', 'test']:
        return ["Unexpected type '{type}' requested"], status.HTTP_400_BAD_REQUEST

    if sample_manager.user_exists(username):
        app.logger.info(f'{type} {username}')
        return {'samples': sample_manager.get_samples(username, type)}, status.HTTP_200_OK
    else:
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST


@app.route("/<string:filetype>/<string:sampletype>/<string:username>/<string:filename>", methods=['GET'])
def handle_get_file(filetype, sampletype, username, filename):
    """
    serve audio sample or json file

    :param filetype: 'audio', 'json'
    :param sampletype: sample set type 'train' or 'test'
    :param username: full or normalized username eg. 'Hugo Kołątaj', 'Stanisław', 'hugo_kolataj'
    :param samplename: full name of requested sample eg. '1.wav', '150.wav'
    """

    # TODO: Verbose endpoint, you end up typing the filename twice,
    #  JSON/test/mikolaj/1.json..

    # check for proper file type
    if filetype not in list(config.ALLOWED_FILES_TO_GET.keys()):
        return [f"Unexpected file type '{filetype}' requested.Expected one of: {list(config.ALLOWED_FILES_TO_GET.keys())}"], \
               status.HTTP_400_BAD_REQUEST

    # check for proper sample set type
    if sampletype not in config.ALLOWED_SAMPLE_TYPES:
        return [f"Unexpected sample type '{sampletype}' requested. Expected one of: {config.ALLOWED_SAMPLE_TYPES}"], \
                status.HTTP_400_BAD_REQUEST

    # check if user exists in samplebase
    if not sample_manager.user_exists(username):
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST

    # check if requested file have allowed extension
    allowed_extensions = config.ALLOWED_FILES_TO_GET[filetype]
    proper_extension, extension = sample_manager.file_has_proper_extension(filename, allowed_extensions)
    if not proper_extension:
        return [f"Accepted extensions for filetype '{filetype}': {allowed_extensions}, but got '{extension}' instead"],\
                status.HTTP_400_BAD_REQUEST

    # check if file exists in samplebase
    if not sample_manager.file_exists(username, sampletype, filename):
        return [f"There is no such sample '{filename}' in users '{username}' {sampletype} samplebase"],\
                status.HTTP_400_BAD_REQUEST

    # serve file
    user_dir = sample_manager.get_user_dirpath(username)
    if sampletype == 'test':
        user_dir = os.path.join(user_dir, sampletype)

    app.logger.info(f"send file '{filename}' from '{user_dir}'")
    return send_from_directory(user_dir, filename, as_attachment=True), status.HTTP_200_OK


@app.route("/plot/<string:sampletype>/<string:username>/<string:samplename>",
           methods=['POST'])
def handle_plot_endpoint(sampletype, username, samplename):
    """
    Create/update and return the requested plot
    Available methods: POST
    The request should send a JSON that contains:
    {
        type: "mfcc",
        file_extension: "png" or "pdf"
    }

    :param sampletype: sample set type 'train' or 'test'
    :param username: full or normalized username eg. 'Hugo Kołątaj', 'Stanisław', 'hugo_kolataj'
    :param samplename: full name of the sample to create plot from, e.g. 1.wav
    """
    # TODO: Perhaps handle both '1.wav' and '1' when new SampleManager is
    #  available
    # TODO: later some kind of smart duplication of this endpoint's steps
    #  alongside with handle_get_file could be done - already tasked

    ALLOWED_PLOT_TYPE = ['mfcc']

    # get the request's JSON or return a 400 if an invalid one/none was passed
    if request.get_json(force=True, cache=True, silent=True) is None:
        return ["No or invalid JSON was passed", status.HTTP_400_BAD_REQUEST]

    sent_json_dict = json.loads(request.get_json())

    if sent_json_dict['type'] not in ALLOWED_PLOT_TYPE:
        return [f"Plot of non-existing type was requested,supported plots {ALLOWED_PLOT_TYPE}",
            status.HTTP_400_BAD_REQUEST]

    if sent_json_dict['file_extension'] not in ALLOWED_PLOT_FILE_EXTENSIONS:
        return ["Plot requested cannot be returned with that file extension,"
                f"supported extensions {ALLOWED_PLOT_FILE_EXTENSIONS}",
            status.HTTP_400_BAD_REQUEST]








    # check for proper file type
    if filetype not in list(config.ALLOWED_FILES_TO_GET.keys()):
        return [f"Unexpected file type '{filetype}' requested.Expected one of: {list(config.ALLOWED_FILES_TO_GET.keys())}"], \
               status.HTTP_400_BAD_REQUEST

    # check for proper sample set type
    if sampletype not in config.ALLOWED_SAMPLE_TYPES:
        return [f"Unexpected sample type '{sampletype}' requested. Expected one of: {config.ALLOWED_SAMPLE_TYPES}"], \
                status.HTTP_400_BAD_REQUEST

    # check if user exists in samplebase
    if not sample_manager.user_exists(username):
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST

    # check if requested file have allowed extension
    allowed_extensions = config.ALLOWED_FILES_TO_GET[filetype]
    proper_extension, extension = sample_manager.file_has_proper_extension(filename, allowed_extensions)
    if not proper_extension:
        return [f"Accepted extensions for filetype '{filetype}': {allowed_extensions}, but got '{extension}' instead"],\
                status.HTTP_400_BAD_REQUEST

    # check if file exists in samplebase
    if not sample_manager.file_exists(username, sampletype, filename):
        return [f"There is no such sample '{filename}' in users '{username}' {sampletype} samplebase"],\
                status.HTTP_400_BAD_REQUEST

    # serve file
    user_dir = sample_manager.get_user_dirpath(username)
    if sampletype == 'test':
        user_dir = os.path.join(user_dir, sampletype)

    app.logger.info(f"send file '{filename}' from '{user_dir}'")
    return send_from_directory(user_dir, filename, as_attachment=True), status.HTTP_200_OK

if __name__ == "__main__":
    app.run(debug=True)
