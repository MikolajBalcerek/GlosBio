import unittest

from pymongo import MongoClient
from werkzeug.datastructures import FileStorage
from sample_manager.SampleManager import SampleManager, UsernameException, DatabaseException
from main import app


class TestSampleManagerSaveToDB(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        temp_app = app
        temp_app.config.from_object('config.TestingConfig')
        self.config = temp_app.config
        self.sm = self.config['SAMPLE_MANAGER']
        self.db_name = self.config['DATABASE_NAME']

    @classmethod
    def tearDownClass(self):
        MongoClient(self.sm.db_url).drop_database(self.db_name)

    def test_fnc_create_user(self):
        pass

    def test_fnc_save_new_sample(self):
        pass

    def test_fnc_save_file_to_db(self):
        pass


class TestSampleManager(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        temp_app = app
        temp_app.config.from_object('config.TestingConfig')
        self.config = temp_app.config
        self.sm = self.config['SAMPLE_MANAGER']
        self.db_name = self.config['DATABASE_NAME']

    @classmethod
    def tearDownClass(self):
        MongoClient(self.sm.db_url).drop_database(self.db_name)

    def test_get_normalized_username(self):
        username_simple = 'Abcd Efgh'
        username_complex = "Aąbc ĆdęŁ Ściąö"

        out_simple = self.sm._get_normalized_username(username_simple)
        out_complex = self.sm._get_normalized_username(username_complex)
        
        self.assertEqual(out_simple, 'abcd_efgh',
                         f"Wrong name normalization: '{username_simple}' --> '{out_simple}'")
        self.assertEqual(out_complex, 'aabc_cdel_sciao',
                         f"Wrong name normalization: '{username_complex}' --> '{out_complex}'")

    def test_fnc_is_db_available(self):
        """
        """
        self.assertTrue(self.sm.is_db_available(),
                        "Database should be available but is_db_available() returned 'False'")
        # print(self.sm_db_down)
        # self.assertFalse(self.sm_db_down.is_db_available(),
        #                  "Database should not be available but is_db_available() returned 'True'")    


'''
SAVE:
    def create_user(self, username: str) -> ObjectId:
    def save_new_sample(self, username: str, set_type: str, file_bytes: bytes, content_type: str) -> str:
    def _save_file_to_db(self, filename: str, file_bytes=None, content_type: str = None):
RETRIVE:
    def get_all_usernames(self) -> list:
    def user_exists(self, username: str) -> bool:
    def sample_exists(self, username: str, set_type: str, samplename: str) -> bool:
    def get_user_sample_list(self, username: str, set_type: str) -> list:
    def get_samplefile(self, username: str, set_type: str, samplename: str):
    def _get_user_mongo_id(self, username: str) -> ObjectId:
    def _get_file_from_db(self, id: ObjectId):
OTHERS:
    def is_db_available(self) -> bool:
    def get_plot_for_sample(self, plot_type: str, set_type: str,
                            username: str, sample_name: str,
                            file_extension: str="png", **parameters) -> BytesIO:  
    def _is_username_valid(self, username: str) -> bool:
    def _is_allowed_file_extension(self, file_type: str) -> bool:
    def _get_normalized_username(self, username: str) -> str:
    def _get_sample_class_document_template(self, username: str) -> dict:
    def _get_sample_file_document_template(self, filename: str, id: ObjectId, rec_speech: str = None) -> dict:
    def _get_next_filename(self, username: str, set_type: str) -> str:

'''



    
    # def test_username_to_dirname_invalid_username(self):
    #     username = 'a ?'
    #     with self.assertRaises(UsernameException) as ctx:
    #         self.sample_manager.username_to_dirname(username)
    #     self.assertIn('Incorrect username "a_?" !', str(ctx.exception))

    # def test_create_user_should_pass(self):
    #     self.sample_manager.create_user(self.username)

    # def test_create_users_should_pass(self):
    #     uname1 = "asd asd"
    #     uname2 = "dasd dasd"
    #     self.sample_manager.create_user(uname1)
    #     self.sample_manager.create_user(uname1)
    #     self.sample_manager.create_user(uname2)

    # def test_user_exists(self):
    #     no = self.sample_manager.user_exists(self.username)
    #     self.assertFalse(no)
    #     self.sample_manager.create_user(self.username)
    #     yes = self.sample_manager.user_exists(self.username)
    #     self.assertTrue(yes)

    # def test_get_all_usernames(self):
    #     uname1 = "Aud asd"
    #     uname2 = "śćą ÜüŹąłä"
    #     unames = [uname1, uname2, self.username]
    #     for uname in unames:
    #         self.sample_manager.create_user(uname)
    #     dirnames = set(['aud_asd', 'sca_uuzala', 'qwe_rty'])
    #     self.assertEqual(dirnames, set(self.sample_manager.get_all_usernames()))

    # def test_add_sample_without_user_should_not_pass(self):
    #     sample = b'aaaaaaaa'
    #     with self.assertRaises(FileNotFoundError):
    #         self.sample_manager.add_sample(self.username, sample)

    # def test_add_sample_should_pass(self):
    #     sample = b'aaaaaa'
    #     self.sample_manager.create_user(self.username)
    #     self.sample_manager.add_sample(self.username, sample)

    # def test_get_samples(self):
    #     self.sample_manager.create_user(self.username)
    #     self.assertEqual([], self.sample_manager.get_samples(self.username))
    #     samples = [b'asdasd', b'bbbbb', b'cccc']
    #     for sample in samples:
    #         self.sample_manager.add_sample(self.username, sample)
    #     self.assertEqual(
    #         ['1.wav', '2.wav', '3.wav'],
    #         self.sample_manager.get_samples(self.username)
    #     )

    # def test_get_sample_should_pass(self):
    #     pass

    # def test_get_json_path(self):
    #     example_path_wav = "C:/a.wav"
    #     example_path_webm = "/home/train/5.webm"

    #     suggested_json_path_wav = self.sample_manager.get_new_json_path(
    #         audio_path=example_path_wav)
    #     self.assertEqual(suggested_json_path_wav, "C:/a.json")

    #     suggested_json_path_wav = self.sample_manager.get_new_json_path(
    #         audio_path=example_path_webm)
    #     self.assertEqual(suggested_json_path_wav, "/home/train/5.json")

    # def test_create_json_with_content(self):
    #     """ test for creating a new sample properties json"""
    #     self.sample_manager.create_user("Mikołaj Balcerek")
    #     json_Path = Path(SampleManager.create_a_new_sample_properties_json("Mikołaj Balcerek",
    #                                                       {"recognized_speech": "test"},
    #                                                     self.sample_manager.path+"/mikolaj_balcerek/1.wav"))

    #     self.assertTrue(json_Path.exists(), "Example JSON file was not created")

    #     with json_Path.open(encoding='utf8') as _json_file:
    #         json_dict = json.loads(_json_file.read(), encoding='utf8')
    #         self.assertIn(json_dict["recognized_speech"],
    #                       ["test", 13, '13'],
    #                       "incorrect recognized_speech in JSON")

    #         self.assertEqual(json_dict["name"], "Mikołaj Balcerek",
    #                           "incorrect name in JSON")

    # def test_is_extension_allowed_wav(self):
    #     file = FileStorage(content_type="audio/wav")
    #     self.assertTrue(SampleManager.is_allowed_file_extension(file),
    #                     "file with content type audio/wav was not allowed")

    # def test_is_extension_allowed_webm_disallowed(self):
    #     file = FileStorage(content_type="audio/webm")
    #     self.assertFalse(SampleManager.is_allowed_file_extension(file),
    #                     "file with content type audio/webm was allowed"
    #                     " (should fail the test to be later converted)")

    # def test_get_new_extension_path(self):
    #     path = self.sample_manager._get_new_extension_path("C:/asda.wav", "json")
    #     self.assertEqual("C:/asda.json", path, "Wrong replacement of extension"
    #                                            "in the given path")

    #     path = self.sample_manager._get_new_extension_path("C:\\ad/asd.gpoo",
    #                                                        "pdf")
    #     self.assertEqual("C:\\ad/asd.pdf", path, "Wrong replacement of extension"
    #                                            "in the given path")

    # def test_get_sample_file_name(self):
    #     # TODO some tests for windows - style? Will net to change the underlying
    #     #  _get_sample_file_name_from_path function..

    #     path = self.sample_manager._get_sample_file_name_from_path("/usr/src/axe.gpoo")
    #     self.assertEqual("axe", path,  "Wrong last element of the path returned"
    #                                          "(without extension returned for Linux"
    #                                   "style path")

    #     path = self.sample_manager._get_sample_file_name_from_path("/usr/src/CAPSLOCKED.GPOO")
    #     self.assertEqual("CAPSLOCKED", path,  "Wrong last element of the path returned"
    #                                          "(without extension returned for Linux"
    #                                   "style path with capitalized filename")


    # #TODO: Add a helper function to add a new user with a file
    # Hard to do due to add_sample not being integrated
    # and save_sample requiring FileStorage and overall being a mess


    #TODO: Unit tests for create_new... (json, mfcc_plot)
    # Require the aforementioned helper function
    # For now both are tested using the integration tests

    #TODO: Unit test for _get_wav_sample_expected_file_path
    # Require the aforementioned helper function


if __name__ == '__main__':
    unittest.main()
