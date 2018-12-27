import glob
from pathlib import Path
import unittest
import shutil
import os
import json

from flask_api import status
from pymongo import MongoClient

import config

from main import app
from sample_manager.SampleManager import SampleManager

# SAMPLE_UPLOAD_PATH = config.SAMPLE_UPLOAD_PATH
TEST_USERNAMES = ["Train Person", "Test Person"]
# a nifty search for test audio file that will work both from test dir
# and backend dir
# however will return a false copy if two trzynascie.webm exist
_trzynascie_file_finder_generator = glob.iglob("./**/trzynascie.webm",
                                               recursive=True)
test_audio_path_trzynascie = next(_trzynascie_file_finder_generator)


class Audio_Add_Sample_Tests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        ''' setup before tests_integration form this class '''
        app.config['TESTING'] = True
        self.app = app.test_client()

        self.db_url = f"{config.DATABASE_URL}:{config.DATABASE_PORT}"
        self.db_name = f"{config.DATABASE_NAME}_test"
        self.sm = SampleManager(self.db_url, self.db_name, show_logs=False)

    @classmethod
    def tearDown(self):
        ''' cleanup after every test '''
        client = MongoClient(self.db_url)
        client.drop_database(self.db_name)

    @property
    def client(self):
        """ this is a getter for client """
        return self.app

    def test_post_train_file_username_correct(self):
        """ test for happy path for send file train endpoint """
        with open(test_audio_path_trzynascie, 'rb') as f:
            r = self.client.post('/audio/train',
                                 data={"username": TEST_USERNAMES[0],
                                       "file": f})
            # r type wrappers.Response

            # status code test
            self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                             "wrong status code for file upload")

            # checking whether a person's username was process correctly
            self.assertEqual(r.json["username"], TEST_USERNAMES[0],
                             "wrong username returned for correct upload")

            # check for recognized_speech
            # self.assertIn(r.json["recognized_speech"], ["trzynaście", 13, '13'],
            #               "wrong recognized speech returned for trzynascie")

            # check for existence of new user in db
            _username = r.json["username"]
            self.assertEqual(self.sm.user_exists(_username), True,
                             "User wasn't create")

            # check if sample exists in database in proper sample set
            self.assertEqual(self.sm.sample_exists(_username, "train", "1.wav"), True,
                             "Could not find sample in database")

    def test_post_test_file_username_correct(self):
        """ test for happy path for send file test endpoint """
        with open(test_audio_path_trzynascie, 'rb') as f:
            r = self.client.post('/audio/test',
                                 data={"username": TEST_USERNAMES[1],
                                       "file": f})
            # r type wrappers.Response

            # status code test
            self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                             "wrong status code for file upload")

            # checking whether a person's username was process correctly
            self.assertEqual(r.json["username"], TEST_USERNAMES[1],
                             "wrong username returned for correct upload")

            # check for existence of new user in db
            _username = r.json["username"]
            self.assertEqual(self.sm.user_exists(_username), True,
                             "User wasn't create")

            # check if sample exists in database in proper sample set
            self.assertEqual(self.sm.sample_exists(_username, "test", "1.wav"), True,
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
        with open(test_audio_path_trzynascie, 'rb') as f:
            r = self.client.post('/audio/train',
                                 data={'file': f})
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                             "wrong status code for no username file upload")
            self.assertEqual(r.data, b'["No username"]',
                             "wrong string for lack of username")


class Audio_Get_Sample_Tests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' setup before tests_integration for this class '''
        app.config['TESTING'] = True
        self.app = app.test_client()

        self.db_url = f"{config.DATABASE_URL}:{config.DATABASE_PORT}"
        self.db_name = f"{config.DATABASE_NAME}_test"
        self.sm = SampleManager(self.db_url, self.db_name, show_logs=False)

        with open('./tests_integration/trzynascie.webm', 'rb') as f:
            self.app.post('/audio/train',
                          data={"username": TEST_USERNAMES[0], "file": f})
            f.close()
        with open(test_audio_path_trzynascie, 'rb') as f:
            self.app.post('/audio/test',
                          data={"username": TEST_USERNAMES[1], "file": f})

    @classmethod
    def tearDownClass(self):
        ''' cleanup after every test '''
        client = MongoClient(self.db_url)
        client.drop_database(self.db_name)

    @property
    def client(self):
        """ this is a getter for client """
        return self.app

    def test_get_all_users(self):
        r = self.client.get('/users')

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"wrong status code, expected 200, got {r.status_code}")

        for username in TEST_USERNAMES:
            self.assertIn(username, r.json['users'],
                          f"expected user {username} in all-users list, got: {r.data}")

    def test_get_train_person_sample_list(self):
        r1 = self.client.get(f'/audio/train/{TEST_USERNAMES[0]}')
        r2 = self.client.get(f'/audio/test/{TEST_USERNAMES[0]}')

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

        expected_message = ["There is no such sample '1000.wav' in users 'train_person' train samplebase"]
        self.assertEqual(r.json, expected_message, "expected different message")

        # file doesn't exist - test set
        request_path_4 = f"/audio/test/test_person/1000.wav"
        r = self.client.get(request_path_4)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"request: {request_path_4}\nwrong status code, expected 400, got {r.status_code}")

        expected_message = ["There is no such sample '1000.wav' in users 'test_person' test samplebase"]
        self.assertEqual(r.json, expected_message, "expected different message")

        # user doesn't exist
        request_path_5 = f"/audio/train/mr_nobody12345qwerty/1.wav"
        r = self.client.get(request_path_5)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"request: {request_path_5}\nwrong status code, expected 400, got {r.status_code}")

        expected_message = ["There is no such user 'mr_nobody12345qwerty' in sample base"]
        self.assertEqual(r.json, expected_message, "expected different message")


class PlotEndpointForSampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' setup before tests_integration for this class '''
        app.config['TESTING'] = True
        self.app = app.test_client()
        # self.sm = SampleManager(SAMPLE_UPLOAD_PATH)
        # self.test_dirnames = [self.sm.get_user_dirpath(person) for person in
                              # TEST_USERNAMES]
        self.db_url = f"{config.DATABASE_URL}:{config.DATABASE_PORT}"
        self.db_name = f"{config.DATABASE_NAME}_test"
        self.sm = SampleManager(self.db_url, self.db_name, show_logs=False)

        with open(test_audio_path_trzynascie, 'rb') as f:
            r = self.app.post('/audio/train',
                              data={"username": TEST_USERNAMES[0], "file": f})
            assert r.status_code == status.HTTP_201_CREATED, "wrong status code" \
                                                             " for file upload during class setup"
            f.close()
        with open(test_audio_path_trzynascie, 'rb') as f:
            r = self.app.post('/audio/test',
                              data={"username": TEST_USERNAMES[1], "file": f})
            assert r.status_code == status.HTTP_201_CREATED, "wrong status code" \
                                                             " for file upload during class setup"
            f.close()


    @classmethod
    def tearDownClass(self):
        ''' cleanup after every test '''
        # paths_to_be_deleted = [*self.test_dirnames]
        # for _path in paths_to_be_deleted:
        #     shutil.rmtree(_path)
        client = MongoClient(self.db_url)
        client.drop_database(self.db_name)

    @property
    def client(self):
        """ this is a getter for client """
        return self.app

    def test_GET_mfcc_plot_train_json_no_file_extension_specified(self):
        """ tests for MFCC plot being requested
        with json
        without having specified a file extension
        for an existing user
        in train category """
        request_path = f"/plot/train/{TEST_USERNAMES[0]}/1.wav"
        request_json = json.dumps({"type": "mfcc"})

        r = self.client.get(request_path, json=request_json)

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"request: {request_path} wrong status code, expected 200, got {r.status_code}")

        self.assertEqual(r.content_type, 'image/png',
                         "Wrong content_type was returned"
                         f"for mfcc plot, should be image/png, is {r.content_type}")

        self.assertTrue(len(r.data) > 0,
                         "Generated MFCC plot PNG file from memory is less than 0")

    # def test_GET_mfcc_plot_train_no_json_no_file_extension_specified(self):
    #     """ tests for MFCC plot being requested
    #     without json passed (just correct data in request)
    #     without having specified a file extension
    #     for an existing user
    #     in train category """
    #     request_path = f"/plot/train/{TEST_USERNAMES[0]}/1.wav"

    #     r = self.client.post(request_path, data={"type": "mfcc"})

    #     self.assertEqual(r.content_type, 'image/png',
    #                      "Wrong content_type was returned"
    #                      f"for mfcc plot, should be image/png, is {r.content_type}")

    #     self.assertTrue(len(r.data) > 0,
    #                     "Generated MFCC plot PNG file from memory is less than 0")

    # TODO: tests for pdf
    # TODO: tests for test endpoint
    def test_failing_lack_of_data_url_specified(self):
        """ tests for a post being send to plot endpoint
        without any data specified, but with a correct url """
        request_path = f"/plot/train/{TEST_USERNAMES[0]}/1.wav"

        r = self.client.get(request_path)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, r.status_code,
                         "lack of type (no data) specified when querying plot endpoint "
                         "should result in a failure")

    def test_failing_empty_json_url_specified(self):
        """ tests for a post being send to plot endpoint
        with an empty json file, but with a correct url """
        request_path = f"/plot/train/{TEST_USERNAMES[0]}/1.wav"

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

        self.assertEqual([f"There is no such user '{username}' in sample base"],
                         r.json, "Differing string returned for bad username")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, r.status_code,
                         "Nonexisting username should return 400 during plots")

    # TODO: duplication of tests from other endpoints
    def test_nonexisting_sample_requested_to_plot(self):
        """ tests for a post being send to plot endpoint
        with non-existing file, but with a correct existing username"""
        sample_name = "2.wav"
        user_name = TEST_USERNAMES[0]
        type = 'train'
        request_path = f"/plot/{type}/{user_name}/2.wav"
        request_json = json.dumps({"type": "mfcc"})

        r = self.client.get(request_path, json=request_json)

        self.assertEqual([f"There is no such sample '{sample_name}' in users '{user_name}' {type} samplebase"],
                         r.json, "Differing string returned for bad username")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, r.status_code,
                         "Nonexisting filename for existing user should return 400 during plots")

    def test_incorrect_try_POST_should_405(self):
        """ test for response code on GET request """
        sample_name = "1.wav"
        user_name = TEST_USERNAMES[0]
        type = 'train'
        r = self.client.post(f"/plot/{type}/{user_name}/{sample_name}")

        self.assertEqual(r.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
                         f"Expected resposne status code 405 but got {r.status_code}")
