import glob
import unittest
import json
import abc
from pathlib import Path
from io import BytesIO

import gridfs
from flask_api import status
from pymongo import MongoClient

from main import app
from sample_manager.SampleManager import SampleManager
from algorithms.tests.mocks import TEST_ALG_DICT


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

        self.assertIn('mfcc.png', r.headers.get('Content-Disposition').split("filename=")[1],
                      "mfcc.png filetype not indicated in attachment's filename")

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

        self.assertIn('mfcc.png', r.headers.get('Content-Disposition').split("filename=")[1],
                      "mfcc.png filetype not indicated in attachment's filename")

    def test_GET_spectrogram_plot_train_json_no_file_extension_specified(self):
        """ tests for spectrogram plot being requested
        with json
        without having specified a file extension
        for an existing user
        in train category """
        request_path = f"/plot/train/{self.TEST_USERNAMES[0]}/1.wav"
        request_json = json.dumps({"type": "spectrogram"})

        r = self.client.get(request_path, json=request_json)

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"request: {request_path} wrong status code, expected 200, got {r.status_code}")

        self.assertEqual(r.content_type, 'image/png',
                         "Wrong content_type was returned"
                         f"for spectrogram plot, should be image/png, is {r.content_type}")

        self.assertTrue(len(r.data) > 0,
                        "Generated spectrogram plot PNG file from memory is less than 0")

        self.assertIn('spectrogram.png', r.headers.get('Content-Disposition').split("filename=")[1],
                     "spectrogram.png filetype not indicated in attachment's filename")

    def test_GET_spectrogram_plot_train_no_json_no_file_extension_specified(self):
        """ tests for spectrogram plot being requested
        without json passed (just correct data in request)
        without having specified a file extension
        for an existing user
        in train category """
        request_path = f"/plot/train/{self.TEST_USERNAMES[0]}/1.wav"
        r = self.client.get(request_path, data={"type": "spectrogram"})

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"request: {request_path} wrong status code, expected 200, got {r.status_code}")

        self.assertEqual(r.content_type, 'image/png',
                         "Wrong content_type was returned"
                         f" for spectrogram plot, should be image/png, is {r.content_type}")
        self.assertTrue(len(r.data) > 0,
                        "Generated spectrogram plot PNG file from memory is less than 0")
        self.assertIn('spectrogram.png', r.headers.get('Content-Disposition').split("filename=")[1],
                     "spectrogram.png filetype not indicated in attachment's filename")

    # TODO: tests for pdf MFCC, spectrogram
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

    def test_params_via_query_params(self):
        """ test if passing params via query params works properly """
        sample_name = "1.wav"
        user_name = self.TEST_USERNAMES[0]
        type = 'train'
        request_path = f"/plot/{type}/{user_name}/{sample_name}"
        params = {"type": "mfcc", "file_extension": "pdf"}
        r = self.client.get(request_path, query_string=params)

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"request: {request_path} wrong status code, expected 200, got {r.status_code}")
        self.assertEqual(r.content_type, 'application/pdf',
                         "Wrong content_type was returned"
                         f"for pdf mfcc plot, should be application/pdf, is {r.content_type}")


class TagEndpointsTests(BaseAbstractIntegrationTestsClass):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        # create user:
        self.test_user = "test tags user"
        self.sm.create_user(self.test_user)

        # populate tags
        self.test_tags = {
            "age": ["< 20", "20 - 40", "40 - 60", "> 60"],
            "gender": ["male", "female"],
            "class": ["1", "2", "3"]}
        for tag_name in self.test_tags:
            self.sm.add_tag(tag_name, self.test_tags[tag_name])

        self.test_tags_names = list(self.test_tags.keys())

        self.test_user_tags = {"age": "< 20", "gender": "male"}

        for tag in self.test_user_tags:
            self.sm.add_tag_to_user(self.test_user, tag, self.test_user_tags[tag])

    def test_get_tags(self):
        r = self.client.get('/tag')

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"wrong status code, expected 200, got {r.status_code}")
        self.assertEqual(r.json, self.test_tags_names)

    def test_post_tag(self):
        tag_name = "test_tag"
        wrong_tag_name = "%tag@#$"
        values = ["v1", "v2", "v3"]
        r = self.client.post('/tag', data={"name": tag_name, "values": values})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                         f"wrong status code, expected 201, got {r.status_code}")

        # test same tage second time
        r = self.client.post('/tag', data={"name": tag_name, "values": values})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 201, got {r.status_code}")
        # missing fields
        r = self.client.post('/tag')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")

        # wrong tag name
        r = self.client.post('/tag', data={"name": wrong_tag_name, "values": values})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")

        # empty values
        r = self.client.post('/tag', data={"name": tag_name, "values": []})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")

    def test_get_tag_values(self):
        tag_name = self.test_tags_names[0]
        r = self.client.get(f'/tag/{tag_name}')

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"wrong status code, expected 200, got {r.status_code}")

        self.assertEqual(r.json, self.test_tags[tag_name],
                         f"Expected different tag values")

        r = self.client.get(f'/tag/no-tag')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")

    def test_get_user_tags(self):
        r = self.client.get(f'/users/{self.test_user}/tags')
        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"wrong status code, expected 200, got {r.status_code}")

        self.assertEqual(r.json, self.test_user_tags,
                         f"Expected different user tags")

        r = self.client.get('/users/mr_nobody/tags')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")

    def test_post_user_tags(self):
        proper_tag_name = "class"
        tag_value = self.test_tags[proper_tag_name][0]
        # proper values
        data = {"name": proper_tag_name, "value": tag_value}
        r = self.client.post(f'/users/{self.test_user}/tags', data=data)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                         f"wrong status code, expected 201, got {r.status_code}")

        # try to add same tag twice
        r = self.client.post(f'/users/{self.test_user}/tags', data=data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")
        # invalid username
        r = self.client.post(f'/users/mr_nobody/tags', data=data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")
        # invalid tag name
        data["name"] = "invalid tag"
        r = self.client.post(f'/users/{self.test_user}/tags', data=data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")
        # invalid tag value
        data["name"] = proper_tag_name
        data["value"] = "invalid value"
        r = self.client.post(f'/users/{self.test_user}/tags', data=data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")

    def test_get_user_summary(self):
        r = self.client.get(f'/users/{self.test_user}')
        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"wrong status code, expected 200, got {r.status_code}")

        self.assertTrue(r.data, "Response should not be empty")

        r = self.client.get(f'/users/mr-nobody')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"wrong status code, expected 400, got {r.status_code}")

    def test_get_tags_summary(self):
        r = self.client.get('/summary/tags')
        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"wrong status code, expected 200, got {r.status_code}")

        self.assertTrue(r.data, "Response should not be empty")


class NoDbTests(BaseAbstractIntegrationTestsClass):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        temp_sm = SampleManager(cls.sm.db_url, cls.db_name, show_logs=False)
        temp_sm.db_url = "_____:36363"
        temp_sm.db_client = MongoClient(
            temp_sm.db_url, serverSelectionTimeoutMS=500)
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
        self.am = self.app.config['ALGORITHM_MANAGER']
        self.alg_list = self.am.get_algorithms()
        self.valid_algs = self.alg_list[:-1]
        self.exception_raiser = self.alg_list[-1]

    def tearDown(self):
        for alg_name in self.alg_list:
            path = Path('./algorithms/saved_models/' + alg_name)
            for subpath in path.rglob('*'):
                subpath.rmdir()
            if path.exists():
                path.rmdir()

    def _train_algorithm(self, name):
        params = TEST_ALG_DICT[name].get_parameters()
        some_params = {
            param: params[param]['type'](params[param]['values'][0])
            for param in params.keys()
        }
        data = {'parameters': some_params}
        return self.client.post(f'/algorithms/train/{name}',
                                data=json.dumps(data),
                                content_type='application/json'
                                )

    def test_get_algorithms_names(self):
        self.assertEqual(
            self.client.get('/algorithms').json, {
                'algorithms': self.alg_list,
            })

    def test_get_algorithm_description(self):
        for name in self.valid_algs:
            self.assertEqual(
                self.client.get(f'/algorithms/description/{name}').data,
                TEST_ALG_DICT[name].__doc__.encode() if TEST_ALG_DICT[name].__doc__ else b"",
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
            params = TEST_ALG_DICT[name].get_parameters()
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
        for name in self.alg_list[:-1]:
            r = self._train_algorithm(name)
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
        name = "first_mock"
        r = self.client.post(f'/algorithms/train/{name}',
                             data=json.dumps({}),
                             content_type='application/json'
                             )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, b'Missing "params" field in request body.',
                         'Wrong error message.'
                         )

    def test_train_algorithm_too_many_parameter_keys(self):
        name = self.alg_list[0]
        params = TEST_ALG_DICT[name].get_parameters()
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
        name = self.alg_list[1]
        params = TEST_ALG_DICT[name].get_parameters()
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
        name = "second_mock"
        some_params = {
            'param1': 'not_int',
            'param2': 'whatever'
        }
        data = {'parameters': some_params}
        r = self.client.post(f'/algorithms/train/{name}',
                             data=json.dumps(data),
                             content_type='application/json'
                             )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, b'Bad value type of parameter "param1"',
                         "Should't pass with bad parameter types."
                         )

    def test_train_algorithm_missing_parameters_bad_value(self):
        name = "second_mock"
        some_params = {
            'param1': 10**4,
            'param2': 'c'
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
        for name in self.valid_algs:
            self._train_algorithm(name)
            with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
                data = {'file': f}
                r = self.client.post(f'/algorithms/test/{username}/{name}', data=data)
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            self.assertIn('prediction', r.json)
            if name == 'second_mock':
                self.assertIn('Predicted user', r.json['meta'])
            else:
                self.assertNotIn('Predicted user', r.json['meta'])

    def test_predict_algorithm_no_trained_model(self):
        username = self.TEST_USERNAMES[0]
        for name in self.alg_list:
            with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
                data = {'file': f}
                r = self.client.post(f'/algorithms/test/{username}/{name}', data=data)
            self.assertEqual(r.status_code, 422)
            if name == 'second_mock':
                self.assertEqual(r.data, b'There is no model of second_mock trained.')
            else:
                self.assertNotIn(
                    r.data,
                    f'There is no model of {name} trained for {username}'.encode()
                )

    def test_predict_algorithm_missing_file(self):
        username = self.TEST_USERNAMES[0]
        for name in ['second_mock', 'first_mock']:
            data = {}
            r = self.client.post(f'/algorithms/test/{username}/{name}', data=data)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(r.data, b"No file part")

    def test_predict_algorithm_bad_username(self):
        username = "______thereisnosuchalgname______"
        for name in self.alg_list:
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

    def test_train_algorithm_raising_algorithmexception(self):
        r = self._train_algorithm(self.exception_raiser)
        self.assertEqual(r.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(r.data, b"There was an exception within the algorithm: train exception",
                         'Wrong message returned.'
                         )

    def test_predict_algorithm_raising_algorithmexception(self):

        # make alg_manager think that the model for raise_alg is trained
        base_path = f'./algorithms/saved_models/{self.exception_raiser}/'
        username = self.TEST_USERNAMES[0]
        Path(base_path).mkdir(parents=True)

        with open(self.TEST_AUDIO_PATH_TRZYNASCIE, 'rb') as f:
                data = {'file': f}
                r = self.client.post(f'/algorithms/test/{username}/{self.exception_raiser}', data=data)
        self.assertEqual(r.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(r.data, b"There was an exception within the algorithm: load exception",
                         'Wrong message returned.'
                         )
