import json
import unittest
import shutil
from pathlib import Path

from werkzeug.datastructures import FileStorage
from sample_manager.SampleManager import SampleManager, UsernameException


class TestSampleManager(unittest.TestCase):

    def setUp(self):
        self.sample_manager = SampleManager('./test')
        self.username = "qwe rty"

    def tearDown(self):
        shutil.rmtree('./test', ignore_errors=True)

    def test_username_to_dirname_should_pass(self):
        username = 'Abcd Efgh'
        dirname = self.sample_manager.username_to_dirname(username)
        self.assertEqual(dirname, 'abcd_efgh')

    def test_username_to_dirname_invalid_username(self):
        username = 'a ?'
        with self.assertRaises(UsernameException) as ctx:
            self.sample_manager.username_to_dirname(username)
        self.assertIn('Incorrect username "a_?" !', str(ctx.exception))

    def test_create_user_should_pass(self):
        self.sample_manager.create_user(self.username)

    def test_create_users_should_pass(self):
        uname1 = "asd asd"
        uname2 = "dasd dasd"
        self.sample_manager.create_user(uname1)
        self.sample_manager.create_user(uname1)
        self.sample_manager.create_user(uname2)

    def test_user_exists(self):
        no = self.sample_manager.user_exists(self.username)
        self.assertFalse(no)
        self.sample_manager.create_user(self.username)
        yes = self.sample_manager.user_exists(self.username)
        self.assertTrue(yes)

    def test_get_all_usernames(self):
        uname1 = "Aud asd"
        uname2 = "śćą ÜüŹąłä"
        unames = [uname1, uname2, self.username]
        for uname in unames:
            self.sample_manager.create_user(uname)
        dirnames = set(['aud_asd', 'sca_uuzala', 'qwe_rty'])
        self.assertEqual(dirnames, set(self.sample_manager.get_all_usernames()))

    def test_add_sample_without_user_should_not_pass(self):
        sample = b'aaaaaaaa'
        with self.assertRaises(FileNotFoundError):
            self.sample_manager.add_sample(self.username, sample)

    def test_add_sample_should_pass(self):
        sample = b'aaaaaa'
        self.sample_manager.create_user(self.username)
        self.sample_manager.add_sample(self.username, sample)

    def test_get_samples(self):
        self.sample_manager.create_user(self.username)
        self.assertEqual([], self.sample_manager.get_samples(self.username))
        samples = [b'asdasd', b'bbbbb', b'cccc']
        for sample in samples:
            self.sample_manager.add_sample(self.username, sample)
        self.assertEqual(
            ['1.wav', '2.wav', '3.wav'],
            self.sample_manager.get_samples(self.username)
        )

    def test_get_sample_should_pass(self):
        pass

    def test_get_json_path(self):
        example_path_wav = "C:/a.wav"
        example_path_webm = "/home/train/5.webm"

        suggested_json_path_wav = self.sample_manager._get_new_extension_path(
            audio_path = example_path_wav, format="json")
        self.assertEqual(suggested_json_path_wav, "C:/a.json")

        suggested_json_path_wav = self.sample_manager._get_new_extension_path(
            audio_path=example_path_webm, format="json")
        self.assertEqual(suggested_json_path_wav, "/home/train/5.json")

    def test_create_json_with_content(self):
        """ test for creating a new sample properties json"""
        self.sample_manager.create_user("Mikołaj Balcerek")
        json_Path = Path(self.sample_manager.create_new_sample_properties_json("Mikołaj Balcerek",
                                                                         {"recognized_speech": "test"},
                                                                         self.sample_manager.path +"/mikolaj_balcerek/1.wav"))

        self.assertTrue(json_Path.exists(), "Example JSON file was not created")

        with json_Path.open(encoding='utf8') as _json_file:
            json_dict = json.loads(_json_file.read(), encoding='utf8')
            self.assertIn(json_dict["recognized_speech"],
                          ["test", 13, '13'],
                          "incorrect recognized_speech in JSON")

            self.assertEqual(json_dict["name"], "Mikołaj Balcerek",
                              "incorrect name in JSON")

    def test_is_extension_allowed_wav(self):
        file = FileStorage(content_type="audio/wav")
        self.assertTrue(SampleManager.is_allowed_file_extension(file),
                        "file with content type audio/wav was not allowed")

    def test_is_extension_allowed_webm_disallowed(self):
        file = FileStorage(content_type="audio/webm")
        self.assertFalse(SampleManager.is_allowed_file_extension(file),
                        "file with content type audio/webm was allowed"
                        " (should fail the test to be later converted)")

    def test_get_new_extension_path(self):
        path = self.sample_manager._get_new_extension_path("C:/asda.wav", "json")
        self.assertEqual("C:/asda.json", path, "Wrong replacement of extension"
                                               "in the given path")

        path = self.sample_manager._get_new_extension_path("C:\\ad/asd.gpoo",
                                                           "pdf")
        self.assertEqual("C:\\ad/asd.pdf", path, "Wrong replacement of extension"
                                               "in the given path")

    def test_get_sample_file_name(self):
        path = self.sample_manager._get_sample_file_name_from_path("C:/asda/hellohello.wav")
        self.assertEqual("hellohello", path, "Wrong last element of the path returned"
                                             "(without extension returned for Windows"
                                      "style path with '/'")

        path = self.sample_manager._get_sample_file_name_from_path("C:\\ad\\asd.gpoo")
        self.assertEqual("asd", path,  "Wrong last element of the path returned"
                                             "(without extension returned for Windows"
                                      "style path with '\\'")

        path = self.sample_manager._get_sample_file_name_from_path("/usr/src/axe.gpoo")
        self.assertEqual("axe", path,  "Wrong last element of the path returned"
                                             "(without extension returned for Linux"
                                      "style path")

        path = self.sample_manager._get_sample_file_name_from_path("/usr/src/CAPSLOCKED.GPOO")
        self.assertEqual("CAPSLOCKED", path,  "Wrong last element of the path returned"
                                             "(without extension returned for Linux"
                                      "style path with capitalized filename")


    #TODO: Add a helper function to add a new user with a file
    # Hard to do due to add_sample not being integrated
    # and save_sample requiring FileStorage and overall being a mess


    #TODO: Unit tests for create_new... (json, mfcc_plot)
    # Require the aforementioned helper function
    # For now both are tested using the integration tests

    #TODO: Unit test for _get_sample_file_path
    # Require the aforementioned helper function


if __name__ == '__main__':
    unittest.main()
