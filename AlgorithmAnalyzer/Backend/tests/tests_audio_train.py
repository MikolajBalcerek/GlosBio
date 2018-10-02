from flask_api import status
import requests
import subprocess
import unittest
import sys


class audio_train_endpoint_test(unittest.TestCase):
    def setUp(self):
        """ setup for tests """
        sys.path.append('..')
        subprocess.call("python main.py")

    def test_get_list_audio(self):
        r = requests.get('http://127.0.0.1:5000/audio/train')
        self.assertEqual(r.text, '["hellothere"]',
                         "GET failed, probably was implemented")

    def test_post_file_username_correct(self):
        with open('00001.wav', 'rb') as f:
            r = requests.post('http://127.0.0.1:5000/audio/train',
                          data = {"username" : 'testPerson'},
                              files = {'file': f})
            self.assertEqual(r.status_code, status.HTTP_201_CREATED,
                             "wrong status code for file upload")
            self.assertEqual(r.json()["username"], "testPerson",
                             "wrong username returned for correct upload")

    def test_post_file_no_file(self):
        r = requests.post('http://127.0.0.1:5000/audio/train',
                          data = {"username" : 'testPerson'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                             "wrong status code for lack of file upload")

    def test_post_file_no_username(self):
        with open('00001.wav', 'rb') as f:
            r = requests.post('http://127.0.0.1:5000/audio/train',
                              files = {'file': f})
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST,
                             "wrong status code for no username file upload")


if __name__ == '__main__':
    unittest.main()
