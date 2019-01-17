import glob
import unittest
import json
import abc

import gridfs
from flask_api import status
from pymongo import MongoClient

from sample_manager.SampleManager import SampleManager

from main import app, ALG_DICT


class BaseAbstractIntegrationTestsClass(unittest.TestCase, abc.ABC):

    TEST_USERNAMES = ["Train Person", "Test Person"]
    TEST_AUDIO_PATH_TRZYNASCIE = next(glob.iglob("./**/trzynascie.webm",
                                                 recursive=True))

    @classmethod
    def setUpClass(cls):
        """ setup before tests_integration form this class """
        cls.app = app
        cls.app.config.from_object('config.TestingConfig')
        cls.sm = cls.app.config['SAMPLE_MANAGER']
        cls.db_name = cls.app.config['DATABASE_NAME']
        cls.db_url = cls.sm.db_url
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        """ cleanup after all test cases in a class"""
        MongoClient(cls.db_url).drop_database(cls.db_name)


class AudioAddSampleTests(BaseAbstractIntegrationTestsClass):

    def tearDown(self):
        """ cleanup after each tests"""
        super().tearDownClass()

    def test_post_train_file_username_correct(self):
        """ test for happy path for send file train endpoint """
        with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = self.client.post('/audio/train',
                                 data={"username": self.TEST_USERNAMES[0],
                                       "file": f})
            # r type wrappers.Response

            # status code test
            self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                             "wrong status code for file upload")

            # checking whether a person's username was process correctly
            self.assertEqual(r.json["username"], self.TEST_USERNAMES[0],
                             "wrong username returned for correct upload")

            # check for recognized_speech
            self.assertIn(r.json["recognized_speech"], ["trzynaście", 13, '13'],
                          "wrong recognized speech returned for trzynascie")

            # check for existence of new user in db
            _username = r.json["username"]
            self.assertTrue(self.sm.user_exists(_username),
                            "User wasn't create")

            # check if sample exists in database in proper sample set
            self.assertTrue(self.sm.sample_exists(_username, "train", "1.wav"),
                            "Could not find sample in database")

    def test_post_test_file_username_correct(self):
        """ test for happy path for send file test endpoint """
        with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = self.client.post('/audio/test',
                                 data={"username": self.TEST_USERNAMES[1],
                                       "file": f})
            # r type wrappers.Response

            # status code test
            self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                             "wrong status code for file upload")

            # checking whether a person's username was process correctly
            self.assertEqual(r.json["username"], self.TEST_USERNAMES[1],
                             "wrong username returned for correct upload")

            # check for existence of new user in db
            _username = r.json["username"]
            self.assertTrue(self.sm.user_exists(_username),
                            "User wasn't create")

            # check if sample exists in database in proper sample set
            self.assertTrue(self.sm.sample_exists(_username, "test", "1.wav"),
                            "Could not find sample in database")

    def test_post_file_no_file(self):
        """ test for endpoint send without a file """
        r = self.client.post('/audio/train',
                             data={"username": 'testPerson'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         "wrong status code for lack of file upload")
        self.assertEqual(r.data, b'["No file part"]',
                         "wrong string for lack of file upload")

    def test_post_file_no_username(self):
        """ test for endpoint send without an username """
        with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = self.client.post('/audio/train',
                                 data={'file': f})
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                             "wrong status code for no username file upload")
            self.assertEqual(r.data, b'["Missing \'username\' field in request body"]',
                             "wrong string")

    def test_post_file_special_characters_username(self):
        """ test for endpoint send with invalid username """
        special_char_username = "(();})()=+"

        with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = self.client.post('/audio/train',
                                 data={'username': special_char_username,
                                       'file': f})

            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                             "wrong status code for no username file upload")
            self.assertEqual(r.data, b'["Provided username contains special characters"]',
                             "wrong string")


class AudioGetSampleTests(BaseAbstractIntegrationTestsClass):

    @classmethod
    def setUpClass(cls):
        """ setup before tests_integration for this class """
        super().setUpClass()

        with open(cls.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = cls.client.post(
                '/audio/train', data={"username": cls.TEST_USERNAMES[0], "file": f})
            assert r.status_code == status.HTTP_201_CREATED, \
                f"Failed preparation for tests - adding sample, should return 201, returned {r.status_code}"
            f.close()

        with open(cls.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = cls.client.post('/audio/test',
                                data={"username": cls.TEST_USERNAMES[1], "file": f})
            assert r.status_code == status.HTTP_201_CREATED, \
                f"Failed preparation for tests - adding sample, should return 201, returned {r.status_code}"
            f.close()

    def test_get_all_users(self):
        r = self.client.get('/users')

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"wrong status code, expected 200, got {r.status_code}")

        for username in self.TEST_USERNAMES:
            self.assertIn(username, r.json['users'],
                          f"expected user {username} in all-users list, got: {r.data}")

    def test_get_train_person_sample_list(self):
        r1 = self.client.get(f'/audio/train/{self.TEST_USERNAMES[0]}')
        r2 = self.client.get(f'/audio/test/{self.TEST_USERNAMES[0]}')

        # check status code
        self.assertEqual(r1.status_code, status.HTTP_200_OK,
                         f"wrong status code, expected 200, got {r1.status_code}")
        self.assertEqual(r2.status_code, status.HTTP_200_OK,
                         f"wrong status code, expected 200, got {r2.status_code}")

        self.assertEqual(r1.json['samples'], ['1.wav'],
                         f"expected one sample, got {r1.json['samples']}")

        self.assertEqual(r2.json["samples"], [],
                         f"expected no samples, got {r2.json['samples']}")

    def test_get_samples_for_wrong_user(self):
        r = self.client.get('/audio/train/mr_nobody')

        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")

    def test_get_samples_for_wrong_type(self):
        """ tests for 400 if a bad endpoint is given"""
        r = self.client.get('/random_endpoint_name/train/mr_nobody')

        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND,
                         f"wrong status code, expected 404  , got {r.status_code}")

    # def test_get_json(self):
    #     # file exists
    #     request_path_1 = f"/json/train/{self.sm._get_normalized_username(TEST_USERNAMES[0])}/1.json"
    #     r = self.client.get(request_path_1)
    #     self.assertEqual(r.status_code, status.HTTP_200_OK,
    #                      f"request: {request_path_1}\nwrong status code, expected 200, got {r.status_code}")

    #     # file doesn't exist
    #     request_path_2 = f"/json/train/{self.sm._get_normalized_username(TEST_USERNAMES[0])}/2.json"
    #     r = self.client.get(request_path_2)
    #     self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
    #                      f"request: {request_path_2}\nwrong status code, expected 400, got {r.status_code}")

    #     # file exists but wrong filetype (audio) is applied
    #     request_path_3 = f"/audio/train/{self.sm._get_normalized_username(TEST_USERNAMES[0])}/1.json"
    #     r = self.client.get(request_path_3)
    #     self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
    #                      f"request: {request_path_3} wrong status code, expected 400, got {r.status_code}")

    #     expected_message = [f"Accepted extensions for filetype 'audio': {config.ALLOWED_FILES_TO_GET['audio']}, but got 'json' instead"]
    #     self.assertEqual(r.json, expected_message, "expected different message")

    def test_get_sample(self):
        # file exists - test set
        request_path_1 = f"/audio/test/test_person/1.wav"
        r = self.client.get(request_path_1)
        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"request: {request_path_1}\nwrong status code, expected 200, got {r.status_code}, message: {r.data}")

        # file exists - train set
        request_path_2 = f"/audio/train/train_person/1.wav"
        r = self.client.get(request_path_2)
        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"request: {request_path_2}\nwrong status code, expected 200, got {r.status_code}, message: {r.data}")

        # file doesn't exist - train set
        request_path_3 = f"/audio/train/train_person/1000.wav"
        r = self.client.get(request_path_3)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"request: {request_path_3}\nwrong status code, expected 400, got {r.status_code}")

        expected_message = [
            "There is no such sample '1000.wav' in users 'train_person' train samplebase"]
        self.assertEqual(r.json, expected_message,
                         "expected different message")

        # file doesn't exist - test set
        request_path_4 = f"/audio/test/test_person/1000.wav"
        r = self.client.get(request_path_4)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"request: {request_path_4}\nwrong status code, expected 400, got {r.status_code}")

        expected_message = [
            "There is no such sample '1000.wav' in users 'test_person' test samplebase"]
        self.assertEqual(r.json, expected_message,
                         "expected different message")

        # user doesn't exist
        request_path_5 = f"/audio/train/mr_nobody12345qwerty/1.wav"
        r = self.client.get(request_path_5)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"request: {request_path_5}\nwrong status code, expected 400, got {r.status_code}")

        expected_message = [
            "There is no such user 'mr_nobody12345qwerty' in sample base"]
        self.assertEqual(r.json, expected_message,
                         "expected different message")


class PlotEndpointForSampleTests(BaseAbstractIntegrationTestsClass):

    @classmethod
    def setUpClass(cls):
        """ setup before tests_integration for this class """
        super().setUpClass()
        with open(cls.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = cls.client.post('/audio/train',
                                data={"username": cls.TEST_USERNAMES[0],
                                      "file": f})
            assert r.status_code == status.HTTP_201_CREATED, "wrong status code" \
                                                             " for file upload during class setup"
            f.close()
        with open(cls.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = cls.client.post('/audio/test',
                                data={"username": cls.TEST_USERNAMES[1],
                                      "file": f})
            assert r.status_code == status.HTTP_201_CREATED, "wrong status code" \
                                                             " for file upload during class setup"
            f.close()

    def test_GET_mfcc_plot_train_json_no_file_extension_specified(self):
        """ tests for MFCC plot being requested
        with json
        without having specified a file extension
        for an existing user
        in train category """
        request_path = f"/plot/train/{self.TEST_USERNAMES[0]}/1.wav"
        request_json = json.dumps({"type": "mfcc"})

        r = self.client.get(request_path, json=request_json)

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"request: {request_path} wrong status code, expected 200, got {r.status_code}")

        self.assertEqual(r.content_type, 'image/png',
                         "Wrong content_type was returned"
                         f"for mfcc plot, should be image/png, is {r.content_type}")

        self.assertTrue(len(r.data) > 0,
                        "Generated MFCC plot PNG file from memory is less than 0")

    def test_GET_mfcc_plot_train_no_json_no_file_extension_specified(self):
        """ tests for MFCC plot being requested
        without json passed (just correct data in request)
        without having specified a file extension
        for an existing user
        in train category """
        request_path = f"/plot/train/{self.TEST_USERNAMES[0]}/1.wav"
        r = self.client.get(request_path, data={"type": "mfcc"})

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"request: {request_path} wrong status code, expected 200, got {r.status_code}")

        self.assertEqual(r.content_type, 'image/png',
                         "Wrong content_type was returned"
                         f" for mfcc plot, should be image/png, is {r.content_type}")
        self.assertTrue(len(r.data) > 0,
                        "Generated MFCC plot PNG file from memory is less than 0")

    # TODO: tests for pdf
    # TODO: tests for test endpoint
    def test_failing_lack_of_data_url_specified(self):
        """ tests for a post being send to plot endpoint
        without any data specified, but with a correct url """
        request_path = f"/plot/train/{self.TEST_USERNAMES[0]}/1.wav"

        r = self.client.get(request_path)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, r.status_code,
                         "lack of type (no data) specified when querying plot endpoint "
                         "should result in a failure")

    def test_failing_empty_json_url_specified(self):
        """ tests for a post being send to plot endpoint
        with an empty json file, but with a correct url """
        request_path = f"/plot/train/{self.TEST_USERNAMES[0]}/1.wav"

        empty_json = json.dumps(dict())
        r = self.client.get(request_path, json=empty_json)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, r.status_code,
                         "lack of type (empty json) specified "
                         "when querying plot endpoint should result in a failure")

    # TODO: duplication of tests from other endpoints
    def test_bad_username_specified(self):
        """ tests for a post being send to plot endpoint
        with a correct file, but with an incorrect nonexisting username"""
        username = "random_username"
        request_path = f"/plot/train/{username}/1.wav"
        request_json = json.dumps({"type": "mfcc"})

        r = self.client.get(request_path, json=request_json)

        self.assertEqual(
            [f"There is no such user '{username}' in sample base"],
            r.json, "Differing string returned for bad username")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, r.status_code,
                         "Nonexisting username should return 400 during plots")

    # TODO: duplication of tests from other endpoints
    def test_nonexisting_sample_requested_to_plot(self):
        """ tests for a post being send to plot endpoint
        with non-existing file, but with a correct existing username"""
        sample_name = "2.wav"
        user_name = self.TEST_USERNAMES[0]
        type = 'train'
        request_path = f"/plot/{type}/{user_name}/2.wav"
        request_json = json.dumps({"type": "mfcc"})

        r = self.client.get(request_path, json=request_json)

        self.assertEqual([f"There is no such sample '{sample_name}' in users '{user_name}' {type} samplebase"],

                         r.json, "Differing string returned for bad username")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, r.status_code,
                         "Nonexisting filename for existing user should return 400 during plots")

    def test_incorrect_try_POST_should_405(self):
        """ test for response code on POST request """
        sample_name = "1.wav"
        user_name = self.TEST_USERNAMES[0]
        type = 'train'
        r = self.client.post(f"/plot/{type}/{user_name}/{sample_name}")

        self.assertEqual(r.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
                         f"Expected response status code 405 but got {r.status_code}")


class NoDbTests(BaseAbstractIntegrationTestsClass):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        temp_sm = SampleManager(cls.sm.db_url, cls.db_name, show_logs=False)
        temp_sm.db_url = "_____:36363"
        temp_sm.db_client = MongoClient(
            temp_sm.db_url, serverSelectionTimeoutMS=1000)
        temp_sm.db_database = temp_sm.db_client["unknown_collection"]
        temp_sm.db_collection = temp_sm.db_database.samples
        temp_sm.db_file_storage = gridfs.GridFS(temp_sm.db_database)

        assert not temp_sm.is_db_available(
        ), f"Database '{temp_sm.db_url}' should not be available"

        cls.app.config['SAMPLE_MANAGER'] = temp_sm

    def test_no_db_post_sample(self):
        with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = self.client.post('/audio/train',
                                 data={"username": self.TEST_USERNAMES[0],
                                       "file": f})

            # status code test
            self.assertEqual(r.status_code, status.HTTP_503_SERVICE_UNAVAILABLE,
                             f"wrong status code, expected 503, got {r.status_code}")

    def test_no_db_get_all_users(self):
        r = self.client.get('/users')
        self.assertEqual(r.status_code, status.HTTP_503_SERVICE_UNAVAILABLE,
                         f"wrong status code, expected 503, got {r.status_code}")

    def test_no_db_get_sample_list(self):
        r = self.client.get(f'/audio/train/{self.TEST_USERNAMES[0]}')

        self.assertEqual(r.status_code, status.HTTP_503_SERVICE_UNAVAILABLE,
                         f"wrong status code, expected 503, got {r.status_code}")

    def test_no_db_get_sample(self):
        r = self.client.get(f"/audio/test/test_person/1.wav")
        self.assertEqual(r.status_code, status.HTTP_503_SERVICE_UNAVAILABLE,
                         f"wrong status code, expected 503, got {r.status_code}")

    def test_no_db_get_plot(self):
        request_path = f"/plot/train/{self.TEST_USERNAMES[0]}/1.wav"
        request_json = json.dumps({"type": "mfcc"})

        r = self.client.get(request_path, json=request_json)
        self.assertEqual(r.status_code, status.HTTP_503_SERVICE_UNAVAILABLE,
                         f"wrong status code, expected 503, got {r.status_code}")


class AlgorithmsTests(BaseAbstractIntegrationTestsClass):
    @classmethod
    def setUpClass(cls):
        """ setup before tests_integration for this class """
        super().setUpClass()
        with open(cls.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = cls.client.post('/audio/train',
                                data={"username": cls.TEST_USERNAMES[0],
                                      "file": f})
            assert r.status_code == status.HTTP_201_CREATED, "wrong status code" \
                                                             " for file upload during class setup"
            f.close()
        with open(cls.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            r = cls.client.post('/audio/test',
                                data={"username": cls.TEST_USERNAMES[1],
                                      "file": f})
            assert r.status_code == status.HTTP_201_CREATED, "wrong status code" \
                                                             " for file upload during class setup"
            f.close()

    def setUp(self):
        self.alg_list = list(ALG_DICT.keys())

    def test_get_algorithms_names(self):
        self.assertEqual(
            self.client.get('/algorithms').json, {
                'algorithms': self.alg_list,
            })

    def test_get_algorithm_description(self):
        for name in self.alg_list:
            self.assertEqual(
                self.client.get(f'/algorithms/description/{name}').data,
                ALG_DICT[name].__doc__.encode() if ALG_DICT[name].__doc__ else b"",
                "Bad description returned."
            )

    def test_get_algorithm_description_wrong_name(self):
        name = "______thereisnosuchalgname______"
        self.assertEqual(
                self.client.get(f'/algorithms/description/{name}').status_code,
                status.HTTP_400_BAD_REQUEST,
                "Wrong name should yield bad request."
            )
        self.assertEqual(
                self.client.get(f'/algorithms/description/{name}').data,
                f"Bad algorithm name. Valid are {self.alg_list}.".encode(),
                "Wrong error message."
            )

    def test_get_algorithm_parameters(self):
        for name in self.alg_list:
            params = ALG_DICT[name].get_parameters()
            for param in params:
                params[param].pop('type', None)
            self.assertEqual(
                self.client.get(f'/algorithms/parameters/{name}').json, {
                    'parameters': params
                },
                "Returned and expected parameters didn't match."
            )

    def test_get_algorithm_parameters_wrong_name(self):
        name = "______thereisnosuchalgname______"
        self.assertEqual(
                self.client.get(f'/algorithms/parameters/{name}').status_code,
                status.HTTP_400_BAD_REQUEST,
                "Wrong name should yield bad request."
            )
        self.assertEqual(
                self.client.get(f'/algorithms/parameters/{name}').data,
                f"Bad algorithm name. Valid are {self.alg_list}.".encode(),
                "Wrong error message."
            )

    def test_train_algorithm(self):
        for name in ['Random', 'Multilabel Random']:
            params = ALG_DICT[name].get_parameters()
            some_params = {
                param: params[param]['type'](params[param]['values'][0])
                for param in params.keys()
            }
            data = {'parameters': some_params}
            r = self.client.post(f'/algorithms/train/{name}',
                                 data=json.dumps(data),
                                 content_type='application/json'
                                 )
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            self.assertEqual(r.data, b'Training ended.',
                             'Wrong message returned.'
                             )

    def test_train_algorithm_bad_name(self):
        name = "______thereisnosuchalgname______"
        data = {'parameters': None}
        r = self.client.post(f'/algorithms/train/{name}',
                             data=json.dumps(data),
                             content_type='application/json'
                             )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data,
                         f"Bad algorithm name. Valid are {self.alg_list}.".encode(),
                         'Wrong error message.'
                         )

    def test_train_algorithm_no_parameters(self):
        name = "Random"
        params = ALG_DICT[name].get_parameters()
        some_params = {
            param: params[param]['type'](params[param]['values'][0])
            for param in params.keys()
        }
        data = {'parameters': some_params}
        r = self.client.post(f'/algorithms/train/{name}',
                             data=json.dumps({}),
                             content_type='application/json'
                             )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, b'Missing "params" field in request body.',
                         'Wrong error message.'
                         )

    def test_train_algorithm_too_many_parameter_keys(self):
        name = "Random"
        params = ALG_DICT[name].get_parameters()
        some_params = {
            param: params[param]['type'](params[param]['values'][0])
            for param in params.keys()
        }
        some_params['___bad_name___'] = 'some value'
        data = {'parameters': some_params}
        r = self.client.post(f'/algorithms/train/{name}',
                             data=json.dumps(data),
                             content_type='application/json'
                             )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, b'Bad algorithm parameters.',
                         "Shouldn't pass with too many parameters."
                         )

    def test_train_algorithm_missing_parameters(self):
        name = "Multilabel Random"
        params = ALG_DICT[name].get_parameters()
        some_params = {
            param: params[param]['type'](params[param]['values'][0])
            for param in list(params.keys())[:-1]
        }
        data = {'parameters': some_params}
        r = self.client.post(f'/algorithms/train/{name}',
                             data=json.dumps(data),
                             content_type='application/json'
                             )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, b'Bad algorithm parameters.',
                         "Shouldn't pass with too few parameters."
                         )

    def test_train_algorithm_parameters_bad_type(self):
        name = "Multilabel Random"
        some_params = {
            'num_classes': 'not_int'
        }
        data = {'parameters': some_params}
        r = self.client.post(f'/algorithms/train/{name}',
                             data=json.dumps(data),
                             content_type='application/json'
                             )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, b'Bad value type of parameter "num_classes"',
                         "Should't pass with bad parameter types."
                         )

    def test_train_algorithm_missing_parameters_bad_value(self):
        name = "Multilabel Random"
        some_params = {
            'num_classes': 10**4
        }
        data = {'parameters': some_params}
        r = self.client.post(f'/algorithms/train/{name}',
                             data=json.dumps(data),
                             content_type='application/json'
                             )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, b'At least one parameter has bad value.',
                         "Should't pass with parameter value notin accepted values."
                         )

    def test_predict_algorithm(self):
        username = self.TEST_USERNAMES[0]
        for name in ['Multilabel Random', 'Random']:
            with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
                data = {'file': f}
                r = self.client.post(f'/algorithms/test/{username}/{name}', data=data)
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            self.assertIn('prediction', r.json)
            if name == 'Multilabel Random':
                self.assertIn('Predicted user', r.json['meta'])
            else:
                self.assertNotIn('Predicted user', r.json['meta'])

    def test_predict_algorithm_missing_file(self):
        username = self.TEST_USERNAMES[0]
        for name in ['Multilabel Random', 'Random']:
            data = {}
            r = self.client.post(f'/algorithms/test/{username}/{name}', data=data)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(r.data, b"No file part")

    def test_predict_algorithm_bad_username(self):
        username = "______thereisnosuchalgname______"
        for name in ['Multilabel Random', 'Random']:
            with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
                data = {'file': f}
                r = self.client.post(f'/algorithms/test/{username}/{name}', data=data)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(r.data, b"Such user doesn't exist")

    def test_predict_algorithm_bad_algorithm_ame(self):
        username = self.TEST_USERNAMES[0]
        name = "______thereisnosuchalgname______"
        with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
            data = {'file': f}
            r = self.client.post(f'/algorithms/test/{username}/{name}', data=data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, f"Bad algorithm name. Valid are {self.alg_list}.".encode())
