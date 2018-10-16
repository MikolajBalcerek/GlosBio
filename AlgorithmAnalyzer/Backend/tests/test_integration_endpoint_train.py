from pathlib import Path
import os
import unittest

from flask_api import status
from flask import wrappers

from main import app


class Audio_Train_Unit_Tests(unittest.TestCase):

    test_person_name = "TestPerson"

    def setUp(self):
        """ setup for every test """
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        """ cleanup after each test """
        # delete files made during testing
        my_wav = Path(f"./data/{self.test_person_name}.wav")
        my_webm = Path(f"./data/{self.test_person_name}.webm")

        paths_to_be_deleted = [my_wav, my_webm]
        for _path in paths_to_be_deleted:
            try:
                os.remove(_path)
            except:
                pass


    @property
    def client(self):
        """ this is a getter for client """
        return self.app

    def test_get_list_audio(self):
        r = self.client.get('/audio/train')
        self.assertIn(r.data, b'["hellothere"]',
                         "GET failed, probably was implemented")

    def test_post_file_username_correct(self):
        """ test for happy path for send file train endpoint """
        with open('./tests/trzynascie.webm', 'rb') as f:
            r = self.client.post('/audio/train',
                          data = {"username" : self.test_person_name,
                                 "file" : f})
            #r type wrappers.Response

            # status code test
            self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                             "wrong status code for file upload")

            # checking whether a person's username was process correctly
            self.assertEqual(r.json["username"], self.test_person_name,
                             "wrong username returned for correct upload")

            # check for recognized_speech
            self.assertIn(r.json["recognized_speech"], ["trzynaście" , 13, '13'],
                             "wrong recognized speech returned for trzynascie")

            # check whether webm was converted and saved to wav
            my_wav = Path(f"./data/{self.test_person_name}.wav")
            self.assertEqual(my_wav.exists(), True, "File was not converted and saved as .wav")


    def test_post_file_no_file(self):
        """ test for endpoint send without a file """
        r = self.client.post('/audio/train',
                          data = {"username" : 'testPerson'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                             "wrong status code for lack of file upload")

    def test_post_file_no_username(self):
        """ test for endpoint send without an username """
        with open('./tests/trzynascie.webm', 'rb') as f:
            r = self.client.post('/audio/train',
                              data = {'file': f})
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                             "wrong status code for no username file upload")

