from flask import request, current_app
from flask_api import FlaskAPI, status
from flask_cors import CORS

import urllib

from utils import SampleManager, UsernameException
from speech_recognition_wrapper import speech_to_text_wrapper

UPLOAD_TRAIN_PATH = './train'
app = FlaskAPI(__name__)

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


@app.route("/audio/train", methods=['GET', 'POST'])
def handling_audio_train_endpoint():
    """ This handles generic operations that have to do with audio
    being sent/received from test files

    POST to send a new audio file
    GET to get a list of existing files """

    def allowed_file(name):
        """ some function to see if a name could be used as a file name"""
        return '.' in name and \
               name.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

    if request.method == 'GET':
        # TODO: return all audio train list
        return ["hellothere"]

    if request.method == 'POST':
        if 'file' not in request.files:
            return ['No file part'], status.HTTP_400_BAD_REQUEST
        if 'username' not in request.data:
            return ['No username'], status.HTTP_400_BAD_REQUEST

        username = request.data.get('username')
        file = request.files.get('file')

        sample_manager = SampleManager(UPLOAD_TRAIN_PATH)
        try:
            path, recognized_speech = sample_manager.save_new_sample(username, file)
        except UsernameException:
            return ['Bad username'], status.HTTP_400_BAD_REQUEST


        return {"username": username,
                "text": f"Uploaded file for {username}, "
                        f"recognized: {recognized_speech}",
                "recognized_speech": str(recognized_speech)
        }, status.HTTP_201_CREATED


if __name__ == "__main__":
    app.run(debug=True)
