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


class Audio_Add_Sample_Tests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        ''' setup before tests_integration form this class '''
        app.config['TESTING'] = True
        self.app = app.test_client()

        self.db_url = f"{config.DATABASE_URL}:{config.DATABASE_PORT}"
        self.db_name = f"{config.DATABASE_NAME}_test"
        self.sm = SampleManager(self.db_url, self.db_name, show_logs=False)

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
        with open('./tests_integration/trzynascie.webm', 'rb') as f:
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
            self.assertEqual(self.sm.does_sample_exist(_username, "train", "1.wav"), True,
                             "Could not find sample in database")


    def test_post_test_file_username_correct(self):
        """ test for happy path for send file test endpoint """
        with open('./tests_integration/trzynascie.webm', 'rb') as f:
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
            self.assertEqual(self.sm.does_sample_exist(_username, "test", "1.wav"), True,
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
        with open('./tests_integration/trzynascie.webm', 'rb') as f:
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

        with open('./tests_integration/trzynascie.webm', 'rb') as f:
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
