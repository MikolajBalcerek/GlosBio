import unittest
import abc
import glob
import hashlib

from pymongo import MongoClient
from werkzeug.datastructures import FileStorage
from bson.objectid import ObjectId
from gridfs import GridOut
from io import BytesIO

from sample_manager.SampleManager import SampleManager, UsernameException, DatabaseException
from main import app


class BaseAbstractSampleManagerTestsClass(unittest.TestCase, abc.ABC):
    """ 
    abstract class which is base for all SampleManager test classes
    it provides basic setup and cleanup before and after tests
    """

    # TO DO: move it to test config?
    TEST_AUDIO_WAV_PATH = next(glob.iglob("./**/Kornelia_Cwik.wav",
                               recursive=True))

    TEST_AUDIO_WEBM_PATH = next(glob.iglob("./**/trzynascie.webm",
                                recursive=True))

    @classmethod
    def setUpClass(self):
        """ setup before tests_integration form this class """
        temp_app = app
        temp_app.config.from_object('config.TestingConfig')
        self.config = temp_app.config
        self.sm = self.config['SAMPLE_MANAGER']
        self.db_name = self.config['DATABASE_NAME']

    @classmethod
    def tearDownClass(self):
        """ cleanup after all test cases in a class"""
        MongoClient(self.sm.db_url).drop_database(self.db_name)


class TestSaveToDatabaseFunctions(BaseAbstractSampleManagerTestsClass):
    """ tests for functions related to saving to database """

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.db_collection = self.sm.db_collection
        self.db_fs = self.sm.db_file_storage

    @classmethod
    def tearDown(self):
        super().tearDownClass()

    def test_fnc_create_user(self):
        username = "Test Test"

        # function should return ObjectId
        id_out = self.sm.create_user(username)
        self.assertTrue(isinstance(id_out, ObjectId),
                        "returned value should has type of 'ObjectId, but got '{type(id_out)}' instead")

        # document id database should be created
        db_out = self.db_collection.find_one({'_id': id_out, 'name': "Test Test"})
        self.assertTrue(bool(db_out), "query to database should not return empty result")

        # should not allow to create second user with the same name
        self.assertRaises(UsernameException, self.sm.create_user, username)

    def test_fnc_save_new_sample(self):
        username = "Test Test"
        with open(self.TEST_AUDIO_WEBM_PATH, 'rb') as f:
            self.sm.save_new_sample(username, "train", f.read(), "audio/webm")

        # new user should be created
        db_out = self.db_collection.find_one({'name': username})
        self.assertTrue(bool(db_out), "Query to database should not return empty result")

        # new user document should contain sample in train set
        train_samples = db_out["samples"]["train"]
        self.assertTrue(train_samples, "Could not find added sample in train set")

        # new user document should contain recognizedSpeech field
        self.assertTrue(train_samples[0]["recognizedSpeech"],
                        "Expected recognizedSpeech field to not be empty")
        
        with open(self.TEST_AUDIO_WAV_PATH, 'rb') as f:
            self.sm.save_new_sample(username, "train", f.read(), "audio/wav", recognize=False)

        # should not create second user with same name
        find_count = self.db_collection.count_documents({'name': username})
        self.assertEqual(find_count, 1,
                         "Found {find_count} documents with the same username, but expected only one")

        # should add another sample to train set
        db_out = self.db_collection.find_one({'name': username})
        train_set = db_out["samples"]["train"]
        self.assertEqual(len(train_set), 2,
                         f"Expected to find 2 samples in train set but found {len(train_set)} instead")

    def test_fnc_save_file_to_db(self):
        with open(self.TEST_AUDIO_WAV_PATH, 'rb') as f:
            file_bytes = f.read()
        id_out = self.sm._save_file_to_db("test_file.wav", file_bytes)

        # document should be created
        self.assertTrue(self.db_fs.exists(id_out), "Could not find file in file storage")

        file_obj = self.db_fs.get(id_out)

        # file should not be empty
        self.assertGreater(file_obj.length, 0,
                           "File storege returned empty file")

        # wav file has exacly the same bytes, compare mp5 hashes
        bytes_in_hash = hashlib.md5()
        bytes_in_hash.update(file_bytes)
        
        bytes_out_hash = hashlib.md5()
        bytes_out_hash.update(file_obj.read())

        self.assertEqual(bytes_out_hash.hexdigest(), bytes_in_hash.hexdigest(),
                         "Retrived file differs from orginal one")

        # should have 'audio/x-wav' or 'audio/wav' content type
        self.assertTrue(file_obj.content_type in ["audio/x-wav", "audio/wav"]
                        f"Expected 'audio/x-wav' content type but got '{file_obj.content_type}'")


class TestReadFromDatabaseFunctions(BaseAbstractSampleManagerTestsClass):
    """ tests for functions realted to loading from database """

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.db_collection = self.sm.db_collection

        # populate test collection
        with open(self.TEST_AUDIO_WAV_PATH, 'rb') as f:
            test_file_bytes_wav = f.read()

        with open(self.TEST_AUDIO_WEBM_PATH, 'rb') as f:
            test_file_bytes_webm = f.read()

        username_1 = "Test Username 1"
        username_2 = "Test Username 2"

        self.sm.save_new_sample(username_1, "train", test_file_bytes_wav, "audio/wav", recognize=False)
        self.sm.save_new_sample(username_1, "train", test_file_bytes_webm, "audio/webm", recognize=False)
        self.sm.save_new_sample(username_1, "train", test_file_bytes_wav, "audio/wav", recognize=False)
        self.sm.save_new_sample(username_1, "test", test_file_bytes_webm, "audio/webm", recognize=False)
        self.sm.save_new_sample(username_1, "test", test_file_bytes_wav, "audio/wav", recognize=False)

        self.sm.save_new_sample(username_2, "train", test_file_bytes_webm, "audio/webm", recognize=False)
        self.sm.save_new_sample(username_2, "train", test_file_bytes_wav, "audio/wav", recognize=False)
        
        self.test_usernames = [username_1, username_2]

    def test_fnc_is_db_available(self):
        # db should be available
        self.assertTrue(self.sm.is_db_available(),
                        "Database should be available but is_db_available() returned 'False'")

    def test_fnc_get_all_usernames(self):
        out = self.sm.get_all_usernames()

        # should return list
        self.assertTrue(isinstance(out, list), f"Expected list returned but got '{type(out)}'")

        # list should contain usernames from database
        self.assertEqual(out, self.test_usernames,
                         f"Retrived usernames differ, expected {self.test_usernames}, but got {out}")

    def test_fnc_user_exists(self):
        for username in self.test_usernames:
            self.assertTrue(self.sm.user_exists(username),
                            f"User '{username}' exists in samplebase, but user_exists() returned False")

        # should return false for unknown user
        unknown_user = "Mr Nobody"
        self.assertFalse(self.sm.user_exists(unknown_user),
                         f"There should not be user '{unknown_user}' in samplebase, but user_exists() returned True")

    def test_fnc_sample_exists(self):
        # sample should exist
        out = self.sm.sample_exists(self.test_usernames[0], "test", "1.wav")
        self.assertTrue(out, "Sample exist but sample_exists() returned False")
 
        # sample should does not exist
        out = self.sm.sample_exists(self.test_usernames[0], "test", "10.wav")
        self.assertFalse(out, "Sample does not exist but sample_exists() returned True")

    def test_fnc_get_user_sample_list(self):
        out_train = self.sm.get_user_sample_list(self.test_usernames[0], "train")
        out_test = self.sm.get_user_sample_list(self.test_usernames[0], "test")

        self.assertTrue(isinstance(out_train, list), f"Expected list returned but got '{type(out_train)}'")

        self.assertEqual(len(out_train), 3,
                         f"Expected 3 samplenames in train set but got {len(out_train)}")

        self.assertEqual(len(out_test), 2,
                         f"Expected 2 samplenames in train set but got {len(out_test)}")

        out = self.sm.get_user_sample_list("Mr Nobody", "test")
        self.assertEqual(out, [],
                         f"Expected empty list to be returned, got '{out}' instead")

    def test_fnc_get_samplefile(self):
        out = self.sm.get_samplefile(self.test_usernames[1], "train", "1.wav")

        # returned value should be type of GridOut
        self.assertTrue(isinstance(out, GridOut), "Expected GridOut returned but got '{type(out)}'")

        # file object should contain filename
        self.assertEqual(out.filename, "1.wav",
                         "Wrong filename in returned GridOut object, expected '1.wav', got '{out.filename}'")

        # file object should contain non-empty bytes
        self.assertGreater(out.length, 0,
                           "Returned GridOut should contain non-empty audio bytes")

    def test_fnc_get_user_mongo_id(self):
        out = self.sm._get_user_mongo_id(self.test_usernames[0])
        self.assertTrue(isinstance(out, ObjectId), f"Expected ObjectId returned but got '{type(out)}'")

        # user which does not exist shoud not have id
        out = self.sm._get_user_mongo_id("Mr Nobody")
        self.assertEqual(out, None, f"Got id for non-existing user")

    def test_fnc_get_file_from_db(self):
        user_1_doc = self.db_collection.find_one({'name': self.test_usernames[0]})
        user_1_sample = user_1_doc["samples"]["train"][0]

        # should return GridOut
        out = self.sm._get_file_from_db(user_1_sample["id"])
        self.assertTrue(isinstance(out, GridOut), f"Expected GridOut returned but got '{type(out)}'")

        # should contain non empty bytes
        self.assertGreater(out.length, 0,
                           "Returned GridOut should contain non-empty audio bytes")

    def test_fnc_get_plot_for_sample(self):
        # check for every possible plot type
        for plot_type in self.sm.ALLOWED_PLOT_TYPES_FROM_SAMPLES:
            out = self.sm.get_plot_for_sample(plot_type, "train", self.test_usernames[0], "1.wav")

            # returned value should be instance of BytesIO
            self.assertTrue(isinstance(out, bytes), f"Expected bytes returned but got '{type(out)}'")

            # should contain nonempty bytes
            self.assertGreater(len(out), 0,
                               "Returned BytesIO should contain non-empty bytes")

        # should throw ValueError for unknown plot type
        args = ["unknown_plot_type", "train", self.test_usernames[0], "1.wav"]
        self.assertRaises(ValueError, self.sm.get_plot_for_sample, *args)

        # should return None if sample, set or username does not exist
        out = self.sm.get_plot_for_sample("mfcc", "train", self.test_usernames[0], "10.wav")
        self.assertEqual(out, None, f"Expected returned value to be None but it has type of '{type(out)}'")

    def test_fnc_get_next_filename(self):
        out = self.sm._get_next_filename(self.test_usernames[0], "test")
        self.assertEqual(out, '3.wav',
                         f"Next proper name is '3.wav', got '{out}' instead")

        out = self.sm._get_next_filename(self.test_usernames[0], "train")
        self.assertEqual(out, '4.wav',
                         f"Next proper name is '4.wav', got '{out}' instead")

        out = self.sm._get_next_filename(self.test_usernames[1], "test")
        self.assertEqual(out, '1.wav',
                         f"Next proper name is 1.wav', got '{out}' instead")

        out = self.sm._get_next_filename("Mr Nobody", "train")
        self.assertEqual(out, '1.wav',
                         f"Next proper name is 1.wav', got '{out}' instead")

class TestSampleManager(BaseAbstractSampleManagerTestsClass):
    """ tests for functions which do not operate on database """

    def test_fnc_get_normalized_username(self):
        username_simple = 'Abcd Efgh'
        username_complex = "Aąbc ĆdęŁ Ściąö"
        username_special = "{}*=+ ///---.?"

        out_simple = self.sm._get_normalized_username(username_simple)
        out_complex = self.sm._get_normalized_username(username_complex)
        
        self.assertEqual(out_simple, 'abcd_efgh',
                         f"Wrong name normalization: '{username_simple}' --> '{out_simple}'")
        self.assertEqual(out_complex, 'aabc_cdel_sciao',
                         f"Wrong name normalization: '{username_complex}' --> '{out_complex}'")

        self.assertRaises(UsernameException, self.sm._get_normalized_username, username_special)

    def test_fnc_is_allowed_file_extension(self):
        self.assertTrue(self.sm._is_allowed_file_extension("audio/wav"),
                        "Expected True returned for 'audio/wav'")
        self.assertFalse(self.sm._is_allowed_file_extension("audio/unknown"),
                         "Expected False returned for unknown file extension")

    def test_fnc_get_sample_class_document_template(self):
        out = self.sm._get_sample_class_document_template("user")
        expected_fields = set(['name', 'nameNormalized', 'created', 'samples', 'tags'])

        self.assertEqual(set(out.keys()), expected_fields,
                         f"Expected fields: {expected_fields}, but got {out.keys()}")

    def test_fnc_get_sample_file_document_template(self):
        out = self.sm._get_sample_file_document_template('1.wav', ObjectId('555fc7956cda204928c9dbab'))
        expected_fields = set(['id', 'filename', 'recognizedSpeech'])

        self.assertEqual(set(out.keys()), expected_fields,
                         f"Expected fields: {expected_fields}, but got {out.keys()}")


if __name__ == '__main__':
    unittest.main()
