from pathlib import Path
import unittest
import shutil
import os
import json


from flask_api import status

import config
from main import app
from sample_manager.SampleManager import SampleManager



SAMPLE_UPLOAD_PATH = config.SAMPLE_UPLOAD_PATH
TEST_USERNAMES = ["Train Person", "Test Person"]


class Audio_Add_Sample_Tests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        ''' setup before tests_integration form this class '''
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.sm = SampleManager(SAMPLE_UPLOAD_PATH)
        self.test_dirnames = [self.sm.get_user_dirpath(person) for person in TEST_USERNAMES]

    def tearDown(self):
        ''' cleanup after every test '''
        paths_to_be_deleted = [*self.test_dirnames]
        for _path in paths_to_be_deleted:
            if os.path.exists(_path):
                shutil.rmtree(_path)

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
            self.assertIn(r.json["recognized_speech"], ["trzynaście", 13, '13'],
                          "wrong recognized speech returned for trzynascie")

            # check for existence of JSON file
            _json_path = Path(f"{SAMPLE_UPLOAD_PATH}/{self.sm.username_to_dirname(TEST_USERNAMES[0])}/1.json")
            self.assertEqual(_json_path.exists(), True,
                             "Sample was not accompanied by .json file")

            # check whether JSON includes name and recognized_speech

            with open(_json_path, 'r') as _json_file:
                json_dict = json.loads(_json_file.read(), encoding='utf8')
                self.assertIn(json_dict["recognized_speech"], ["trzynaście", 13, '13'],
                              "incorrect recognized_speech in JSON")

                self.assertEqual(json_dict["name"], TEST_USERNAMES[0],
                                 "incorrect name in JSON")

            # check whether webm was converted and saved to wav
            new_wav_expected_path = os.path.join(self.test_dirnames[0], '1.wav')
            my_wav = Path(new_wav_expected_path)
            self.assertEqual(my_wav.exists(), True,
                             "File was not converted and saved as .wav")

            # check for mfcc .png plot file
            new_mfcc_expected_path = os.path.join(self.test_dirnames[0], '1.png')
            mfcc_file = Path(new_mfcc_expected_path)
            self.assertEqual(mfcc_file.exists(), True,
                             "MFCC .png was not created")

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

            # check whether webm was converted and saved to wav
            new_wav_expected_path = os.path.join(self.test_dirnames[1], 'test', '1.wav')
            my_wav = Path(new_wav_expected_path)
            self.assertEqual(my_wav.exists(), True,
                             f"Missing converted .wav file in '{self.test_dirnames[1]}/test' directory")

            # check for existence of JSON file
            _json_path = Path(f"{SAMPLE_UPLOAD_PATH}/{self.sm.username_to_dirname(TEST_USERNAMES[1])}/test/1.json")
            self.assertEqual(_json_path.exists(), True,
                             "Sample was not accompanied by .json file")

            # check for existence of MFCC plot file
            _mfcc_plot_path = Path(
                f"{SAMPLE_UPLOAD_PATH}/{self.sm.username_to_dirname(TEST_USERNAMES[1])}/test/1.png")
            self.assertEqual(_json_path.exists(), True,
                             "Sample was not accompanied by MFCC plot .png file")


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
        self.sm = SampleManager(SAMPLE_UPLOAD_PATH)
        self.test_dirnames = [self.sm.get_user_dirpath(person) for person in TEST_USERNAMES]
        with open('./tests_integration/trzynascie.webm', 'rb') as f:
            self.app.post('/audio/train',
                          data={"username": TEST_USERNAMES[0], "file": f})
            f.close()
        with open('./tests_integration/trzynascie.webm', 'rb') as f:
            self.app.post('/audio/test',
                          data={"username": TEST_USERNAMES[1], "file": f})
            f.close()

    @classmethod
    def tearDownClass(self):
        ''' cleanup after every test '''
        paths_to_be_deleted = [*self.test_dirnames]
        for _path in paths_to_be_deleted:
            shutil.rmtree(_path)

    @property
    def client(self):
        """ this is a getter for client """
        return self.app

    def test_get_all_users(self):
        r = self.client.get('/users')
        expected_usrnames = set([self.sm.username_to_dirname(p) for p in TEST_USERNAMES])

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"wrong status code, expected 200, got {r.status_code}")

        for username in expected_usrnames:
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

    def test_get_json(self):
        # file exists
        request_path_1 = f"/json/train/{self.sm.username_to_dirname(TEST_USERNAMES[0])}/1.json"
        r = self.client.get(request_path_1)
        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         f"request: {request_path_1}\nwrong status code, expected 200, got {r.status_code}")

        # file doesn't exist
        request_path_2 = f"/json/train/{self.sm.username_to_dirname(TEST_USERNAMES[0])}/2.json"
        r = self.client.get(request_path_2)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"request: {request_path_2}\nwrong status code, expected 400, got {r.status_code}")

        # file exists but wrong filetype (audio) is applied
        request_path_3 = f"/audio/train/{self.sm.username_to_dirname(TEST_USERNAMES[0])}/1.json"
        r = self.client.get(request_path_3)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         f"request: {request_path_3}\nwrong status code, expected 400, got {r.status_code}")
        
        expected_message = [f"Accepted extensions for filetype 'audio': {config.ALLOWED_FILES_TO_GET['audio']}, but got 'json' instead"]
        self.assertEqual(r.json, expected_message, "expected different message")

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
