import urllib

from flask import request, current_app, send_file
from flask_api import FlaskAPI, status
from flask_cors import CORS
from io import BytesIO

import config
from sample_manager.SampleManager import SampleManager, UsernameException

app = FlaskAPI(__name__)
sample_manager = SampleManager(f"{config.DATABASE_URL}:{config.DATABASE_PORT}", config.DATABASE_NAME)

CORS(app)


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
    usernames = sample_manager.get_all_usernames()
    return {'users': usernames}, status.HTTP_200_OK


@app.route("/audio/<string:type>", methods=['POST'])
def handling_audio_endpoint(type):
    """
    This handles generic operations that have to do with audio
    being sent/received from test files

    POST to send a new audio file
    """
    if type not in ['train', 'test']:
        return [f"Unexpected type '{type}' requested"], status.HTTP_400_BAD_REQUEST

    if 'file' not in request.files:
        return ['No file part'], status.HTTP_400_BAD_REQUEST

    if 'username' not in request.data:
        return ['No username'], status.HTTP_400_BAD_REQUEST

    app.logger.info(f"add new sample to {type} set")
    username = request.data.get('username')
    file = request.files.get('file')

    try:
        recognized_speech = sample_manager.save_new_sample(username, type, file)
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
        return {'samples': sample_manager.get_user_sample_list(username, type)}, status.HTTP_200_OK
    else:
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST


@app.route("/audio/<string:sampletype>/<string:username>/<string:samplename>", methods=['GET'])
def handle_get_file(sampletype, username, samplename):
    """
    serve audio sample or json file

    sampletype: sample set type 'train' or 'test'
    username: full or normalized username eg. 'Hugo Kołątaj', 'Stanisław', 'hugo_kolataj'
    samplename: full name of requested sample eg. '1', '150'
    """

    # check for proper sample set type
    if sampletype not in config.ALLOWED_SAMPLE_TYPES:
        return [f"Unexpected sample type '{sampletype}' requested. Expected one of: {config.ALLOWED_SAMPLE_TYPES}"], \
                status.HTTP_400_BAD_REQUEST

    # check if user exists in samplebase
    if not sample_manager.user_exists(username):
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST

    # check if requested file have allowed extension
    # allowed_extensions = config.ALLOWED_FILES_TO_GET[filetype]
    # proper_extension, extension = sample_manager.file_has_proper_extension(filename, allowed_extensions)
    # if not proper_extension:
    #     return [f"Accepted extensions for filetype '{filetype}': {allowed_extensions}, but got '{extension}' instead"],\
    #             status.HTTP_400_BAD_REQUEST

    file = sample_manager.get_samplefile(username, sampletype, samplename)

    # check if file exists in samplebase
    if not file:
        return [f"There is no such sample '{samplename}' in users '{username}' {sampletype} samplebase"],\
                status.HTTP_400_BAD_REQUEST

    app.logger.info(f"send file '{samplename}' from database")
    return send_file(BytesIO(file.read()), mimetype=file.content_type)


if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "main":
    # to set proper database name during tests
    sample_manager = SampleManager(f"{config.DATABASE_URL}:{config.DATABASE_PORT}",
                                   f"{config.DATABASE_NAME}_test",
                                   show_logs=False)
