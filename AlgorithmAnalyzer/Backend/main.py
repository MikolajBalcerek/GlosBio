from flask import request, current_app, send_from_directory
from flask_api import FlaskAPI, status
from flask_cors import CORS

import urllib

from utils import SampleManager, UsernameException

SAMPLE_UPLOAD_PATH = './data'
app = FlaskAPI(__name__)
sample_manager = SampleManager(SAMPLE_UPLOAD_PATH)

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
    return {'users': sample_manager.get_all_usernames()}, status.HTTP_200_OK


@app.route("/audio/<string:type>", methods=['POST'])
def handling_audio_endpoint(type):
    """
    This handles generic operations that have to do with audio
    being sent/received from test files

    POST to send a new audio file
    """

    # def allowed_file(name):
    #     """ some function to see if a name could be used as a file name"""
    #     return '.' in name and \
    #            name.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

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


@app.route("/audio/<string:type>/<string:username>/<string:samplename>", methods=['GET'])
def handle_get_sample(type, username, samplename):
    """
    serve sample .wav as static file

    type: sample set type 'train' or 'test'
    username: full name, eg. 'Hugo Kołątaj' or 'Stanisław'
    samplename: full name of requested sample eg. '1.wav', '150.wav'
    """
    if type not in ['train', 'test']:
        return [f"Unexpected type '{type}' requested"], status.HTTP_400_BAD_REQUEST

    elif not sample_manager.user_exists(username):
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST

    elif not sample_manager.sample_exists(username, type, samplename):
        return [f"There is no such sample '{samplename}' in users '{username}' {type} samplebase"], status.HTTP_400_BAD_REQUEST

    else:
        user_dir = sample_manager.get_user_dirpath(username)
        app.logger.info(f"send file '{samplename}' from '{user_dir}'")
        return send_from_directory(user_dir, samplename, as_attachment=True), status.HTTP_200_OK


if __name__ == "__main__":
    app.run(debug=True)
