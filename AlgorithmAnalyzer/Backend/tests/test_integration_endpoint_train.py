from pathlib import Path
import unittest
import shutil
import os

from flask_api import status
from flask import wrappers
from utils import SampleManager

from main import app

SAMPLE_UPLOAD_PATH = './data'
sample_manager = SampleManager(SAMPLE_UPLOAD_PATH)


class Audio_Train_Unit_Tests(unittest.TestCase):
    test_person_name = "Test Person"
    test_person_dir = sample_manager.get_user_dirpath(test_person_name)

    def setUp(self):
        """ setup for every test """
        # nie lepiej ustawiać tego w setUpClass()?
        app.config['TESTING'] = True
        self.app = app.test_client()

    @classmethod
    def tearDownClass(cls):
        """ clean dirs created during tests """
        paths_to_be_deleted = [cls.test_person_dir]
        for _path in paths_to_be_deleted:
            print("#INFO: delete {} directory after test".format(_path))
            shutil.rmtree(_path)

    @property
    def client(self):
        """ this is a getter for client """
        return self.app

    def test_get_list_audio(self):
        r = self.client.get('/audio/train')
        self.assertEqual(r.status_code, status.HTTP_200_OK,
                         "wrong status code, expected 200, got {}".format(r.status_code))

    def test_post_file_username_correct(self):
        """ test for happy path for send file train endpoint """
        with open('./tests/trzynascie.webm', 'rb') as f:
            r = self.client.post('/audio/train',
                                 data={"username": self.test_person_name,
                                       "file": f})
            # r type wrappers.Response

            # status code test
            self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                             "wrong status code for file upload")

            # checking whether a person's username was process correctly
            self.assertEqual(r.json["username"], self.test_person_name,
                             "wrong username returned for correct upload")

            # check for recognized_speech
            self.assertIn(r.json["recognized_speech"], ["trzynaście", 13, '13'],
                          "wrong recognized speech returned for trzynascie")

            # check whether webm was converted and saved to wav
            new_wav_expected_path = os.path.join(self.test_person_dir, '1.wav')
            my_wav = Path(new_wav_expected_path)
            self.assertEqual(my_wav.exists(), True, "File was not converted and saved as .wav")

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
