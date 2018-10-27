from flask import request, current_app, send_from_directory
from flask_api import FlaskAPI, status
from flask_cors import CORS

import speech_recognition as sr
import urllib
import os

from utils import SampleManager, UsernameException
from speech_recognition_wrapper import speech_to_text_wrapper
from convert_audio_wrapper import convert_webm

SAMPLE_UPLOAD_PATH = './data'
ALLOWED_AUDIO_EXTENSIONS = set(['wav', 'flac', 'webm'])
app = FlaskAPI(__name__)
sample_manager = SampleManager(SAMPLE_UPLOAD_PATH)

CORS(app)


def set_sample_base_dir(path):
    SAMPLE_UPLOAD_PATH = path
    global sample_manager
    sample_manager = SampleManager(SAMPLE_UPLOAD_PATH)


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


@app.route("/audio/<type>", methods=['POST'])
def handling_audio_endpoint(type):
    """
    This handles generic operations that have to do with audio
    being sent/received from test files

    POST to send a new audio file
    """

    def allowed_file(name):
        """ some function to see if a name could be used as a file name"""
        return '.' in name and \
               name.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

    if type not in ['train', 'test']:
        return ["Unexpected type '{}' requested".format(type)], status.HTTP_400_BAD_REQUEST

    if request.method == 'POST':
        if 'file' not in request.files:
            return ['No file part'], status.HTTP_400_BAD_REQUEST
        if 'username' not in request.data:
            return ['No username'], status.HTTP_400_BAD_REQUEST
        app.logger.info("add new sample to {} set".format(type))
        username = request.data.get('username')
        file = request.files.get('file')

        # TO DO: sprawdzanie czy FileStorage zawiera mime type z ALLOWED_AUDIO_EXTENSIONS
        try:
            path = sample_manager.save_new_sample(username, file, type)
            app.logger.info(".webm file saved to: {}".format(path))
        except UsernameException:
            return ['Bad username'], status.HTTP_400_BAD_REQUEST

        # TO DO: zawinąć konwerter w try - catch
        convert_webm.convert_webm_to_format(
            path, path.replace(".webm", ""), "wav")
        app.logger.info("file copy converted to wav")

        with sr.AudioFile(path.replace(".webm", ".wav")) as converted_file:
            recognized_speech = speech_to_text_wrapper.recognize_speech(
                converted_file)
            app.logger.info(f'Recognized words: "{recognized_speech}"')

        return {"username": username,
                "text": f"Uploaded file for {username}, "
                        f"recognized: {recognized_speech}",
                "recognized_speech": str(recognized_speech)
                }, status.HTTP_201_CREATED


@app.route("/audio/<type>/<username>", methods=['GET'])
def handle_list_samples_for_user(type, username):
    """
    it handles request for listing samples from train or test set
    for particular user

    type: sample set type (train or test)
    username: full name, eg. Hugo Kołątaj or Stanisław
    """
    if type not in ['train', 'test']:
        return ["Unexpected type '{}' requested".format(type)], status.HTTP_400_BAD_REQUEST

    if sample_manager.user_exists(username):
        app.logger.info('{} {}'.format(type, username))
        return {'samples': sample_manager.get_samples(username, type)}, status.HTTP_200_OK
    else:
        return ["There is no such user '{}' in sample base".format(username)], status.HTTP_400_BAD_REQUEST

@app.route("/audio/<type>/<username>/<sample>", methods=['GET'])
def handle_get_sample(type, username, sample):
    """
    serve sample as static file
    """
    if type not in ['train', 'test']:
        return ["Unexpected type '{}' requested".format(type)], status.HTTP_400_BAD_REQUEST

    elif not sample_manager.user_exists(username):
        return ["There is no such user '{}' in sample base".format(username)], status.HTTP_400_BAD_REQUEST

    elif not sample_manager.sample_exists(username, type, sample):
        return ["There is no such sample '{}' in users '{}' {} samplebase".format(sample, username, type)], status.HTTP_400_BAD_REQUEST

    else:
        user_dir = sample_manager.get_user_dirpath(username)
        app.logger.info("send file '{}' from '{}'".format(sample, user_dir))
        return send_from_directory(user_dir, sample, as_attachment=True), status.HTTP_200_OK


if __name__ == "__main__":
    app.run(debug=True)

