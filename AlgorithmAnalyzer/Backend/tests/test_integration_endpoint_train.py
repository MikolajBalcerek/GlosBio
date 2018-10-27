from pathlib import Path
import unittest
import shutil
import os

from flask_api import status
from flask import wrappers
from utils import SampleManager

from main import app

SAMPLE_UPLOAD_PATH = './data'
sm = SampleManager(SAMPLE_UPLOAD_PATH)
test_usernames = ["Train Person", "Test Person"]
test_dirnames = [sm.get_user_dirpath(person) for person in test_usernames]


def tearDownModule():
    paths_to_be_deleted = [*test_dirnames]
    for _path in paths_to_be_deleted:
        print("#INFO: delete {} directory after test".format(_path))
        shutil.rmtree(_path)


class Audio_Add_Sample_Tests(unittest.TestCase):

    def setUp(self):
        """ setup for every test """
        # nie lepiej ustawiać tego w setUpClass()?
        app.config['TESTING'] = True
        self.app = app.test_client()

    @property
    def client(self):
        """ this is a getter for client """
        return self.app

    def test_post_train_file_username_correct(self):
        """ test for happy path for send file train endpoint """
        with open('./tests/trzynascie.webm', 'rb') as f:
            r = self.client.post('/audio/train',
                                 data={"username": test_usernames[0],
                                       "file": f})
            # r type wrappers.Response

            # status code test
            self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                             "wrong status code for file upload")

            # checking whether a person's username was process correctly
            self.assertEqual(r.json["username"], test_usernames[0],
                             "wrong username returned for correct upload")

            # check for recognized_speech
            self.assertIn(r.json["recognized_speech"], ["trzynaście", 13, '13'],
                          "wrong recognized speech returned for trzynascie")

            # check whether webm was converted and saved to wav
            new_wav_expected_path = os.path.join(test_dirnames[0], '1.wav')
            my_wav = Path(new_wav_expected_path)
            self.assertEqual(my_wav.exists(), True,
                             "File was not converted and saved as .wav")

    def test_post_test_file_username_correct(self):
        """ test for happy path for send file test endpoint """
        with open('./tests/trzynascie.webm', 'rb') as f:
            r = self.client.post('/audio/test',
                                 data={"username": test_usernames[1],
                                       "file": f})
            # r type wrappers.Response

            # status code test
            self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                             "wrong status code for file upload")

            # checking whether a person's username was process correctly
            self.assertEqual(r.json["username"], test_usernames[1],
                             "wrong username returned for correct upload")

            # check whether webm was converted and saved to wav
            new_wav_expected_path = os.path.join(test_dirnames[1], 'test', '1.wav')
            my_wav = Path(new_wav_expected_path)
            self.assertEqual(my_wav.exists(), True,
                             "Missing converted .wav file in '{test_dirnames[1]}/test' direcotry")

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
        with open('./tests/trzynascie.webm', 'rb') as f:
            r = self.client.post('/audio/train',
                                 data={'file': f})
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                             "wrong status code for no username file upload")
            self.assertEqual(r.data, b'["No username"]',
                             "wrong string for lack of username")


class Audio_Get_Sample_Tests(unittest.TestCase):

    @property
    def client(self):
        """ this is a getter for client """
        return app.test_client()

    def test_get_all_users(self):
        r = self.client.get('/users')
        expected_usrnames = set([sm.username_to_dirname(p) for p in test_usernames])

        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         "wrong status code, expected 200, got {}".format(r.status_code))

        self.assertEqual(set(r.json['users']), expected_usrnames,
                         "expected list with two usernames, got: {}".format(r.data))

    def test_get_train_person_samples(self):
        r1 = self.client.get('/audio/train/{}'.format(test_usernames[0]))
        r2 = self.client.get('/audio/test/{}'.format(test_usernames[0]))

        # check status code
        self.assertEqual(r1.status_code, status.HTTP_200_OK,
                         "wrong status code, expected 200, got {}".format(r1.status_code))
        self.assertEqual(r2.status_code, status.HTTP_200_OK,
                         "wrong status code, expected 200, got {}".format(r2.status_code))

        self.assertEqual(r1.json['samples'], ['1.wav'],
                         "expected one sample, got {}".format(r1.json['samples']))

        self.assertEqual(r2.json["samples"], [],
                         "expected no samples, got {}".format(r2.json['samples']))

    def test_get_samples_for_wrong_user(self):
        r = self.client.get('/audio/train/mr_nobody')

        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                         "wrong status code, expected 400, got {}".format(r.status_code))
