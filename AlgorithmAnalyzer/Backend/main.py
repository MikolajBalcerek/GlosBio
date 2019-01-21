import io
import urllib
import json
from io import BytesIO

from flask import request, current_app, send_file, jsonify
from flask_api import FlaskAPI, status
from flask_cors import CORS
from functools import wraps

from algorithms.algorithm_manager import NotTrainedException
from algorithms.base_algorithm import AlgorithmException
from sample_manager.SampleManager import SampleManager, UsernameException, DatabaseException
from utils import convert_audio

app = FlaskAPI(__name__)

CORS(app)

# TODO: Would be nice to reword endpoints to follow username -> type instead of
#  type -> username for consistency to how currently SampleManager stores them


def requires_db_connection(f):
    """
    decorator function for routes where database connection can occur
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except DatabaseException as e:
            # hide logs during tests
            if not app.config['TESTING']:
                app.logger.error("Database is unavailable...", e)
        return ["Database is unavailable, try again later"], status.HTTP_503_SERVICE_UNAVAILABLE
    return wrapped


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
@requires_db_connection
def handle_users_endpoint():
    """
    serve list of registered users
    """
    return {'users': app.config['SAMPLE_MANAGER'].get_all_usernames()}, status.HTTP_200_OK


@app.route('/algorithms', methods=['GET'])
def get_algorithms_names():
    """
    Returns the list of names of all algorithms available.
    """
    return {'algorithms': app.config['ALGORITHM_MANAGER'].get_algorithms()}, status.HTTP_200_OK


@app.route('/algorithms/description/<string:name>', methods=['GET'])
def get_algorithm_description(name):
    """
    Returns the description of the algorithm with name <string:name>.
    """
    valid_names = app.config['ALGORITHM_MANAGER'].get_algorithms()
    if name not in valid_names:
        return f'Bad algorithm name. Valid are {valid_names}.', status.HTTP_400_BAD_REQUEST

    description = app.config['ALGORITHM_MANAGER'](name).get_description()
    return description if description else "", status.HTTP_200_OK


@app.route('/algorithms/parameters/<string:name>', methods=['GET'])
def get_algorithm_parameters(name):
    """
    Return all parameters of a given algorithm in the form:
        {'parameter_name': {
            'description': 'A description.',
            'values': [list of possible values]
            }
        }
    <string:name> is the name of the algorithm.
    """
    valid_names = app.config['ALGORITHM_MANAGER'].get_algorithms()
    if name not in valid_names:
        return f'Bad algorithm name. Valid are {valid_names}.', status.HTTP_400_BAD_REQUEST

    return {'parameters': app.config['ALGORITHM_MANAGER'].get_parameters(name)}, status.HTTP_200_OK


@app.route('/algorithms/train/<string:name>', methods=['POST'])
@requires_db_connection
def train_algorithm(name):
    """
    Starts to train the algorithm with name <string:name>.
    Request's data should containt the parameters in the form
        {'parameter_name': 'value'}
    Where the paremeter names and values should agree with the
    output of GET /algorithm/parameters/<string:name>.
    """
    if 'parameters' not in request.data:
        return 'Missing "params" field in request body.', status.HTTP_400_BAD_REQUEST

    valid_names = app.config['ALGORITHM_MANAGER'].get_algorithms()
    if name not in valid_names:
        return f'Bad algorithm name. Valid are {valid_names}.', status.HTTP_400_BAD_REQUEST

    params = request.data['parameters']
    params_legend = app.config['ALGORITHM_MANAGER'].get_parameters(name)

    if set(params.keys()) != set(params_legend.keys()):
        return 'Bad algorithm parameters.', status.HTTP_400_BAD_REQUEST

    params_types = app.config['ALGORITHM_MANAGER'].get_parameter_types(name)

    for param in params:
        try:
            params_types[param](params[param])
        except (ValueError, TypeError):
            return f'Bad value type of parameter "{param}"', status.HTTP_400_BAD_REQUEST

    if any(params_types[key](params[key]) not in params_legend[key]['values'] for key in params):
        return 'At least one parameter has bad value.', status.HTTP_400_BAD_REQUEST

    alg_manager = app.config['ALGORITHM_MANAGER'](name)

    samples, labels = app.config['SAMPLE_MANAGER'].get_all_samples(
        purpose='train',
        multilabel=alg_manager.multilabel,
        sample_type='wav'
    )
    try:
        app.config['ALGORITHM_MANAGER'](name).train(samples, labels, params)
    except AlgorithmException as e:
        return f"There was an exception within the algorithm: {str(e)}", status.HTTP_503_SERVICE_UNAVAILABLE
    return "Training ended.", status.HTTP_200_OK


@app.route('/algorithms/test/<string:user_name>/<string:algorithm_name>', methods=['POST'])
@requires_db_connection
def predict_algorithm(user_name, algorithm_name):
    """
    Uses the algorithm with name <string:algorithm_name> to predict,
    if the wav sent in request.files contains the voice of the user
    with name <string:user_name>. Returns a json of the form
        {
            "prediction": "the result of prediction - true / false",
            "meta": {"key": "value" additional data returned by the algorithm}
        }
    where the additional data may contain things like probabilities etc.
    """
    if 'file' not in request.files:
        return 'No file part', status.HTTP_400_BAD_REQUEST

    valid_names = app.config['ALGORITHM_MANAGER'].get_algorithms()
    if algorithm_name not in valid_names:
        return f'Bad algorithm name. Valid are {valid_names}.', status.HTTP_400_BAD_REQUEST

    if not app.config['SAMPLE_MANAGER'].user_exists(user_name):
        return "Such user doesn't exist", status.HTTP_400_BAD_REQUEST

    file = request.files.get('file')
    if not app.config['SAMPLE_MANAGER'].is_allowed_file_extension(file.mimetype):
        file = convert_audio.convert_audio_to_format(BytesIO(file.read()),  "wav")

    alg_manager = app.config['ALGORITHM_MANAGER'](algorithm_name)

    try:
        prediction, meta = alg_manager.predict(user_name, file)
    except AlgorithmException as e:
            return f"There was an exception within the algorithm: {str(e)}", status.HTTP_503_SERVICE_UNAVAILABLE
    except NotTrainedException as e:
            return str(e), 422

    if alg_manager.multilabel:
        try:
            meta['Predicted user'] = \
                app.config["SAMPLE_MANAGER"].user_numbers_to_usernames([prediction])[0]
        except IndexError:
            prediction = False
            meta['Predicted user'] = 'Algorithm has predicted a nonexisting user.'
        else:
            prediction = meta['Predicted user'] == user_name
    return {"prediction": prediction, 'meta': meta}, status.HTTP_200_OK


@app.route('/algorithms/test_all/<string:algorithm_name>', methods=['POST', 'GET'])
@requires_db_connection
def test_algorithm(algorithm_name):
    """
    Creates the confussion matrix of an algorithm with name <string:algorithm_name>.
    Optionally, request's body may contain field 'users' with a list of usernames,
    for which to compute the matrix.
    If algorithm is not multilabel, returns a list lists:
        [[username, sample_number, fake (T/F), prediction (T/F)]]
    If algorithm is multilabel, returns:
        {
            'users': [list of usernames],
            'matrix': [[matrix as lists of lists]]
        }
    in that case, the last column counts predictions that don't give any user.
    """
    valid_names = app.config['ALGORITHM_MANAGER'].get_algorithms()
    if algorithm_name not in valid_names:
        return f'Bad algorithm name. Valid are {valid_names}.', status.HTTP_400_BAD_REQUEST
    if 'users' in request.data:
        users = request.data['users']
    else:
        users = app.config['SAMPLE_MANAGER'].get_all_usernames()
    try:
        numbers = app.config['SAMPLE_MANAGER'].usernames_to_user_numbers(users)
    except ValueError:
        return "Incorrect username!", status.HTTP_400_BAD_REQUEST

    alg_manager = app.config['ALGORITHM_MANAGER'](algorithm_name)

    samples, labels = app.config['SAMPLE_MANAGER'].get_all_samples(
        purpose='test',
        multilabel=alg_manager.multilabel,
        sample_type='wav'
    )

    try:
        result = alg_manager.test(samples, labels, users, numbers)
    except NotTrainedException as e:
        return str(e), 422

    return result, status.HTTP_200_OK


@app.route("/audio/<string:type>", methods=['POST'])
@requires_db_connection
def handling_audio_endpoint(type):
    """
    This handles generic operations that have to do with audio
    being sent/received from test files

    POST to send a new audio file
    <string:type> should be either 'train' or 'test';
    Requests body should contain 'username' and optionally 'fake'.
    The last should be true/false depending on the sample being real.
    """
    if type not in ['train', 'test']:
        return [f"Unexpected type '{type}' requested"], status.HTTP_400_BAD_REQUEST

    if 'file' not in request.files:
        return ['No file part'], status.HTTP_400_BAD_REQUEST

    if 'username' not in request.data:
        return ["Missing 'username' field in request body"], status.HTTP_400_BAD_REQUEST

    app.logger.info(f"try to add new sample to {type} set")
    username = request.data.get('username')
    file = request.files.get('file')

    fake = False
    if 'fake' in request.data:
        fake = request.data['fake']

    try:
        recognized_speech = app.config['SAMPLE_MANAGER'].save_new_sample(
            username, type, file.read(), fake=fake, content_type=file.mimetype)
    except UsernameException:
        return ['Provided username contains special characters'], status.HTTP_400_BAD_REQUEST

    app.logger.info(f"new sample added successfully")
    return {"username": username,
            "text": f"Uploaded file for {username}, "
                    f"recognized: '{recognized_speech}'",
            "recognized_speech": recognized_speech
            }, status.HTTP_201_CREATED


@app.route("/audio/<string:type>/<string:username>", methods=['GET'])
@requires_db_connection
def handle_list_samples_for_user(type, username):
    """
    it handles request for listing samples from train or test set
    for particular user

    type: sample set type (train or test)
    username: full name, eg. Hugo Kołątaj or Stanisław
    """
    if type not in ['train', 'test']:
        return ["Unexpected type '{type}' requested"], status.HTTP_400_BAD_REQUEST

    if app.config['SAMPLE_MANAGER'].user_exists(username):
        app.logger.info(f'{type} {username}')
        return {'samples': app.config['SAMPLE_MANAGER'].get_user_sample_list(username, type)}, status.HTTP_200_OK
    else:
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST


@app.route("/audio/<string:sampletype>/<string:username>/<string:samplename>", methods=['GET', 'DELETE'])
@requires_db_connection
def handle_get_file(sampletype, username, samplename):
    """
    GET
    serve audio sample audio file

    DELETE
    remove audio file from samplebase

    :param sampletype: sample set type 'train' or 'test'
    :param username: full or normalized username eg. 'Hugo Kołątaj', 'Stanisław', 'hugo_kolataj'
    :param samplename: full name of requested sample eg. '1.wav', '150.wav'
    """
    if request.method == 'DELETE':
        try:
            app.config['SAMPLE_MANAGER'].delete_sample(username, sampletype, samplename)
            return "", status.HTTP_204_NO_CONTENT
        except ValueError as e:
            return [str(e)], status.HTTP_400_BAD_REQUEST
            
    # check for proper sample set type
    if sampletype not in app.config['ALLOWED_SAMPLE_TYPES']:
        return [f"Unexpected sample type '{sampletype}' requested. Expected one of: {app.config['ALLOWED_SAMPLE_TYPES']}"], \
            status.HTTP_400_BAD_REQUEST

    # check if user exists in samplebase
    if not app.config['SAMPLE_MANAGER'].user_exists(username):
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST

    # check if requested file have allowed extension
    # allowed_extensions = config.ALLOWED_FILES_TO_GET[filetype]
    # proper_extension, extension = sample_manager.file_has_proper_extension(filename, allowed_extensions)
    # if not proper_extension:
    #     return [f"Accepted extensions for filetype '{filetype}': {allowed_extensions}, but got '{extension}' instead"],\
    #             status.HTTP_400_BAD_REQUEST

    # get file from samplebase and convert in to mp3
    file = app.config['SAMPLE_MANAGER'].get_samplefile(
        username, sampletype, samplename)

    # check if file exists in samplebase
    if not file:
        return [f"There is no such sample '{samplename}' in users '{username}' {sampletype} samplebase"],\
            status.HTTP_400_BAD_REQUEST

    file_mp3 = convert_audio.convert_audio_to_format(source=file, format="mp3")
    app.logger.info(f"send file '{samplename}' from database")
    return send_file(BytesIO(file_mp3.read()), mimetype=file.content_type)


@app.route("/plot/<string:sampletype>/<string:username>/<string:samplename>",
           methods=['GET'])
@requires_db_connection
def handle_plot_endpoint(sampletype, username, samplename):
    """
    return the requested plot
    Available methods: GET
    The request should send a JSON that contains:
    {
        type: "mfcc", or "spectrogram"
        file_extension: "png" or "pdf"
    }
    or send HTTP POST request which contains the same values as DATA

    :param sampletype: sample set type 'train' or 'test'
    :param username: full or normalized username eg. 'Hugo Kołątaj', 'Stanisław', 'hugo_kolataj'
    :param samplename: full name of the sample to create plot from, e.g. 1.wav
    """

    # TODO: later some kind of smart duplication of this endpoint's steps
    #  alongside with handle_get_file could be done - already tasked

    # get the request's JSON from query params or body
    sent_args = request.args.to_dict()
    if not sent_args:
        try:
            sent_args = json.loads(request.data)
        except TypeError:
            sent_args = request.data
        except Exception:
            return ["Failed to parse request body or params"], status.HTTP_400_BAD_REQUEST

    # return a 400 if an invalid one/none was passed
    if not sent_args:
        return ["Expected field 'type' specified in request body or params"], status.HTTP_400_BAD_REQUEST
    # check for type
    if not sent_args['type']:
        return [f"Missing 'type' field in request body or query params"],\
            status.HTTP_400_BAD_REQUEST
    plot_type = sent_args.get('type')
    if plot_type not in SampleManager.ALLOWED_PLOT_TYPES_FROM_SAMPLES:
        return [f"Plot of non-existing type ('{sent_args.get('type')}') was requested, supported plots {SampleManager.ALLOWED_PLOT_TYPES_FROM_SAMPLES}"], status.HTTP_400_BAD_REQUEST

    # check for file_extension
    if sent_args.get('file_extension') not in SampleManager.ALLOWED_PLOT_FILE_EXTENSIONS:
        if sent_args.get('file_extension') is None:
            sent_args['file_extension'] = 'png'
        else:
            return ["Plot requested cannot be returned with that file extension,"
                    f"supported extensions {SampleManager.ALLOWED_PLOT_FILE_EXTENSIONS}"],\
                status.HTTP_400_BAD_REQUEST

    # TODO: duplication from other endpoints
    # check if user exists in samplebase
    if not app.config['SAMPLE_MANAGER'].user_exists(username):
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST

    # TODO: duplication from other endpoints
    # check if file exists in samplebase
    if not app.config['SAMPLE_MANAGER'].sample_exists(username, sampletype, samplename):
        return [f"There is no such sample '{samplename}' in users '{username}' {sampletype} samplebase"],\
            status.HTTP_400_BAD_REQUEST
    file_bytes, mimetype, plot_filename = app.config['SAMPLE_MANAGER'].get_plot_for_sample(plot_type=sent_args['type'],
                                                                            set_type=sampletype,
                                                                            username=username,
                                                                            sample_name=samplename,
                                                                            file_extension=sent_args['file_extension'])

    # TODO: if a SM rework fails, sending file with the attachment_filename
    #  can be replaced with just plot_path instead of file
    return send_file(io.BytesIO(file_bytes),
                     mimetype=mimetype, as_attachment=True, attachment_filename=plot_filename),\
        status.HTTP_200_OK


@app.route("/tag", methods=['GET', 'POST'])
@requires_db_connection
def handle_tag_entdpoint():
    """
    GET
    will return list with all possible tags

    POST
    {
        name: <tag_name>
        values: [<value_1>, <value_2>, ...]
    }
    will add new tag to tagbase with its possible values
    """
    if request.method == "GET":
        tag_list = app.config['SAMPLE_MANAGER'].get_all_tags()
        return tag_list, status.HTTP_200_OK

    if request.method == "POST":
        for field in ["name", "values"]:
            if field not in request.data:
                return [f"Did not find '{field}' field in request body"], status.HTTP_400_BAD_REQUEST
        # contain some special characters
        name = request.data['name']
        values = request.data['values']
        if app.config['SAMPLE_MANAGER'].tag_exists(name):
            return [f"Tag '{name}' already exists in tag base"], status.HTTP_400_BAD_REQUEST
        try:
            app.config['SAMPLE_MANAGER'].add_tag(name, values)
        except ValueError as e:
            return [f"Cound not add tag, couse: '{str(e)}'"], status.HTTP_400_BAD_REQUEST
        return [f"Added tag '{name}'"], status.HTTP_201_CREATED


@app.route("/tag/<string:tag>", methods=['GET', 'DELETE'])
@requires_db_connection
def handle_tag_value_entdpoint(tag):
    """
    GET
    will list tag possible values

    DELETE
    will delete tag (if it's not in use)
    """
    if not app.config['SAMPLE_MANAGER'].tag_exists(tag):
        return [f"Tag '{tag}' does not exist in tag base"], status.HTTP_400_BAD_REQUEST

    if request.method == 'GET':
        return app.config['SAMPLE_MANAGER'].get_tag_values(tag), status.HTTP_200_OK

    if request.method == 'DELETE':
        try:
            app.config['SAMPLE_MANAGER'].delete_tag(tag)
            return "", status.HTTP_204_NO_CONTENT
        except ValueError as e:
            return [str(e)], status.HTTP_400_BAD_REQUEST


@app.route("/users/<string:username>/tags", methods=['GET', 'POST'])
@requires_db_connection
def handle_user_tags_endpoint(username):
    """
    GET
    list all users' tags

    {
        <tag_1>: <value_1>,
        <tag_2>: <value_2>,
        ...
    }

    POST
    {
        name: <tag_name>
        value: <tag_value>
    }
    will add new tag to users' tag list
    """
    # check if user exists
    if not app.config['SAMPLE_MANAGER'].user_exists(username):
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST

    if request.method == 'GET':
        tags = app.config['SAMPLE_MANAGER'].get_user_tags(username)
        return tags, status.HTTP_200_OK

    if request.method == 'POST':
        for field in ["name", "value"]:
            if field not in request.data:
                return [f"Did not find '{field}' field in request body"], status.HTTP_400_BAD_REQUEST
        tag_name = request.data['name']
        tag_value = request.data['value']

        # check if tag exists
        if not app.config['SAMPLE_MANAGER'].tag_exists(tag_name):
            return [f"Tag '{tag_name}' does not exist in tagbase"], status.HTTP_400_BAD_REQUEST

        # check if tag has proper value
        all_tag_values = app.config['SAMPLE_MANAGER'].get_tag_values(tag_name)
        if tag_value not in all_tag_values:
            return [f"Wrong tag value: '{tag_value}', expected one of: {all_tag_values}"], status.HTTP_400_BAD_REQUEST

        # check if user does already have this tag
        if app.config['SAMPLE_MANAGER'].user_has_tag(username, tag_name):
            return [f"User '{username}' already has tag '{tag_name}'"], status.HTTP_400_BAD_REQUEST

        app.config['SAMPLE_MANAGER'].add_tag_to_user(
            username, tag_name, tag_value)

        return [f"Added tag '{tag_name}' to user '{username}'"], status.HTTP_201_CREATED


@app.route("/users/<string:username>/tags/<string:tag>", methods=['DELETE'])
@requires_db_connection
def handle_delete_user_tag_endpoint(username, tag):
    """
    delete tag fron users tags
    """
    try:
        app.config['SAMPLE_MANAGER'].delete_user_tag(username, tag)
        return "", status.HTTP_204_NO_CONTENT
    except ValueError as e:
        return [str(e)], status.HTTP_400_BAD_REQUEST


@app.route("/users/<string:username>", methods=['GET', 'DELETE'])
@requires_db_connection
def handle_user_summary_endpoint(username):
    """
    GET
    will return user samplebase summary:
      - name
      - normalized name
      - date of creation
      - tags
      - count of samples from test and train sets

    DELETE
    will remove user from samplebase along with all samples
    """
    # check if user exists
    if not app.config['SAMPLE_MANAGER'].user_exists(username):
        return [f"There is no such user '{username}' in sample base"], status.HTTP_400_BAD_REQUEST

    if request.method == 'GET':
        return app.config['SAMPLE_MANAGER'].get_user_summary(username)

    if request.method == 'DELETE':
        try:
            app.config['SAMPLE_MANAGER'].delete_user(username)
            return "", status.HTTP_204_NO_CONTENT
        except ValueError as e:
            return [str(e)], status.HTTP_400_BAD_REQUEST



@app.route("/summary/tags", methods=['GET'])
@requires_db_connection
def handle_tags_summary():
    """
    will return summary of all tags across samplebase
    """
    summary = app.config['SAMPLE_MANAGER'].get_tags_summary()
    return summary, status.HTTP_200_OK



if __name__ == "__main__":
    app.config.from_object('config.DevelopmentConfig')
    app.run()
