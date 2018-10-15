import urllib

from flask import request, url_for, redirect, Flask, current_app
from flask_api import FlaskAPI, status, exceptions, renderers, decorators
from flask_cors import CORS

from utils import SampleManager, UsernameException

UPLOAD_TRAIN_PATH = './train'
ALLOWED_AUDIO_EXTENSIONS = set(['wav', 'mp3'])
app = FlaskAPI(__name__)

CORS(app)


@app.route("/", methods=['GET'])
def landing_documentation_page():
    """ Landing page for browsable API """

    def list_routes():
        """ helper function that returns all routes in a list """
        output = {}
        for rule in app.url_map.iter_rules():
            methods = ', '.join(rule.methods)
            output[urllib.parse.unquote(rule.endpoint)] = {
                "name": urllib.parse.unquote(rule.endpoint),
                "description": " ".join(
                    current_app.view_functions[rule.endpoint].__doc__.split()
                ),
                "methods": urllib.parse.unquote(methods),
                "url":
                    urllib.parse.unquote(str(request.host_url))[0:-1]
                    + str(rule)
            }

        return output

    if request.method == 'GET':
        """ this will list on routes the default endpoint """
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

        # TO DO: sprawdzanie czy FileStorage zawiera mime type z ALLOWED_AUDIO_EXTENSIONS
        sample_manager = SampleManager(UPLOAD_TRAIN_PATH)
        try:
            sample_manager.create_user(username)
        except UsernameException:
            return ['Bad username'], status.HTTP_400_BAD_REQUEST
        path = sample_manager.get_new_sample_path(username)
        file.save(path)
        print("#LOG File saved to: " + path)
        # if file and allowed_file(file.filename):
        #     # final_file_name = /
        #     # filename = secure_filename(jakasnazwastring)
        #     # file.save(os.path.join(app.config['UPLOAD_TRAIN_PATH'], filename))
        #     pass

        return {
                    "username": username,
                    "text": f"Uploaded file for {username}"
                }, status.HTTP_201_CREATED


# @app.route("/<int:key>/", methods=['GET', 'PUT', 'DELETE'])
# def notes_detail(key):
#     """
#     Retrieve, update or delete note instances.
#     """
#     if request.method == 'PUT':
#         note = str(request.data.get('text', ''))
#         notes[key] = note
#         return note_repr(key)
#
#     elif request.method == 'DELETE':
#         notes.pop(key, None)
#         return '', status.HTTP_204_NO_CONTENT
#
#     # request.method == 'GET'
#     if key not in notes:
#         raise exceptions.NotFound()
#     return note_repr(key)


if __name__ == "__main__":
    app.run(debug=True)
