import unittest
import abc
import glob
import hashlib

from pymongo import MongoClient
from bson.objectid import ObjectId
from gridfs import GridOut

from sample_manager.SampleManager import UsernameException
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
        """ setup before tests_integration from this class """
        app.config.from_object('config.TestingConfig')
        self.config = app.config
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
        self.db_tags = self.sm.db_tags

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
        db_out = self.db_collection.find_one(
            {'_id': id_out, 'name': "Test Test"})
        self.assertTrue(
            bool(db_out), "query to database should not return empty result")

        # should not allow to create second user with the same name
        self.assertRaises(UsernameException, self.sm.create_user, username)

    def test_fnc_save_new_sample(self):
        username = "Test Test"
        with open(self.TEST_AUDIO_WEBM_PATH, 'rb') as f:
            self.sm.save_new_sample(username, "train", f.read(), "audio/webm", fake=False)

        # new user should be created
        db_out = self.db_collection.find_one({'name': username})
        self.assertTrue(
            bool(db_out), "Query to database should not return empty result")

        # new user document should contain sample in train set
        train_samples = db_out["samples"]["train"]
        self.assertTrue(
            train_samples, "Could not find added sample in train set")

        # new user document should contain recognizedSpeech field
        self.assertTrue(train_samples[0]["recognizedSpeech"],
                        "Expected recognizedSpeech field to not be empty")

        with open(self.TEST_AUDIO_WAV_PATH, 'rb') as f:
            self.sm.save_new_sample(
                username, "train", f.read(), "audio/wav", fake=False, recognize=False)

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
        self.assertTrue(self.db_fs.exists(id_out),
                        "Could not find file in file storage")

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
        self.assertIn(file_obj.content_type, ["audio/x-wav", "audio/wav"],
                      f"Expected 'audio/x-wav' content type but got '{file_obj.content_type}'")

    def test_fnc_add_tag(self):
        # add valid tags
        name_1 = "tag 1"
        name_2 = "Tag 2"
        values_1 = ["value 1", "value 2"]
        values_2 = ["Value-1", "Value-2", "Value-3"]
        out = self.sm.add_tag(name_1, values_1)
        self.sm.add_tag(name_2, values_2)

        db_out_1 = self.db_tags.find_one({"name": name_1})
        db_out_2 = self.db_tags.find_one({"name": name_2})
        self.assertTrue(db_out_1, f"Could not find added tag {name_1} in tagbase")
        self.assertTrue(db_out_2, f"Could not find added tag {name_2} in tagbase")

        self.assertEqual(db_out_1["values"], values_1, "added tag values differ from oryginal ones")
        self.assertEqual(db_out_2["values"], values_2, "added tag values differ from oryginal ones")

        # add invalid tag (invalid tag name)
        args = ["$invalid()name$", ["val 1", "val 2"]]
        self.assertRaises(ValueError, self.sm.add_tag, *args)

        # add invalid tag (invalid values)
        # args = ["valid name", ["$1**", "$2**"]]
        # self.assertRaises(ValueError, self.sm.add_tag, *args)

    def test_fnc_add_tag_to_user(self):
        # add valid tag (consider it tested)
        tag_name = "valid-tag"
        usernames = ["test tag user 1", "test tag user 2"]
        self.sm.add_tag(tag_name, ["val1", "val2", "val3"])
        self.sm.create_user(usernames[0])
        self.sm.create_user(usernames[1])

        # add tag to user in valid way
        self.sm.add_tag_to_user(usernames[0], tag_name, "val1")
        db_out = self.db_collection.find_one({"name": usernames[0]})
        tags_list = db_out["tags"]

        self.assertEqual(len(tags_list), 1, f"One tag should be added but found {len(tags_list)}")

        tag_obj = tags_list[0]
        self.assertEqual(tag_obj["name"], tag_name,
                         "Expected tag name to be '{tag_name}', but got '{tag_obj['name']}")

        # add same tag in valid way
        args = [usernames[0], tag_name, "val2"]
        self.assertRaises(ValueError, self.sm.add_tag_to_user, *args)

        # add tag to user in invalid way (wrong username, tagname and value)
        args = ["Mr Nobody", tag_name, "val1"]
        self.assertRaises(ValueError, self.sm.add_tag_to_user, *args)

        args = [usernames[1], "no-tag", "val1"]
        self.assertRaises(ValueError, self.sm.add_tag_to_user, *args)

        args = [usernames[1], tag_name, "val100"]
        self.assertRaises(ValueError, self.sm.add_tag_to_user, *args)


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

        # populate samples
        self.sm.save_new_sample(
            username_1, "train", test_file_bytes_wav, "audio/wav", fake=False, recognize=False)
        self.sm.save_new_sample(
            username_1, "train", test_file_bytes_webm, "audio/webm", fake=False, recognize=False)
        self.sm.save_new_sample(
            username_1, "train", test_file_bytes_wav, "audio/wav", fake=True, recognize=False)
        self.sm.save_new_sample(
            username_1, "test", test_file_bytes_webm, "audio/webm", fake=True, recognize=False)
        self.sm.save_new_sample(
            username_1, "test", test_file_bytes_wav, "audio/wav", fake=False, recognize=False)

        self.sm.save_new_sample(
            username_2, "train", test_file_bytes_webm, "audio/webm", fake=True, recognize=False)

        self.sm.save_new_sample(
            username_2, "train", test_file_bytes_wav, "audio/wav", fake=False, recognize=False)

        for i in range(10):
            self.sm.save_new_sample(
                username_2, "test", test_file_bytes_wav, "audio/wav", fake=True, recognize=False)

        self.test_usernames = [username_1, username_2]

        # populate tags
        self.test_tags = {
            "age": ["< 20", "20 - 40", "40 - 60", "> 60"],
            "gender": ["male", "female"]}
        for tag_name in self.test_tags:
            self.sm.add_tag(tag_name, self.test_tags[tag_name])

        # add tags to users
        self.sm.add_tag_to_user(self.test_usernames[0], "age", "< 20")
        # self.sm.add_tag_to_user(self.test_usernames[1], "age", "20 - 40 ")
        self.sm.add_tag_to_user(self.test_usernames[0], "gender", "male")
        # self.sm.add_tag_to_user(self.test_usernames[1], "gender", "female ")

    def test_fnc_is_db_available(self):
        # db should be available
        self.assertTrue(self.sm.is_db_available(),
                        "Database should be available but is_db_available() returned 'False'")

    def test_fnc_get_all_usernames(self):
        out = self.sm.get_all_usernames()

        # should return list
        self.assertTrue(isinstance(out, list),
                        f"Expected list returned but got '{type(out)}'")

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
        self.assertFalse(
            out, "Sample does not exist but sample_exists() returned True")

    def test_fnc_get_user_sample_list(self):
        out_train = self.sm.get_user_sample_list(
            self.test_usernames[0], "train")
        out_test = self.sm.get_user_sample_list(self.test_usernames[0], "test")

        self.assertTrue(isinstance(out_train, list),
                        f"Expected list returned but got '{type(out_train)}'")

        self.assertEqual(len(out_train), 3,
                         f"Expected 3 samplenames in train set but got {len(out_train)}")

        self.assertEqual(len(out_test), 2,
                         f"Expected 2 samplenames in train set but got {len(out_test)}")

        out_test = self.sm.get_user_sample_list(self.test_usernames[1], "test")
        self.assertEqual(len(out_test), 10, f"Expected 10 samplenames in train set but got {len(out_train)}")

        out = self.sm.get_user_sample_list("Mr Nobody", "test")
        self.assertEqual(out, [],
                         f"Expected empty list to be returned, got '{out}' instead")

    def test_fnc_get_samplefile(self):
        out = self.sm.get_samplefile(self.test_usernames[1], "train", "1.wav")

        # returned value should be type of GridOut
        self.assertTrue(isinstance(out, GridOut),
                        "Expected GridOut returned but got '{type(out)}'")

        # file object should contain filename
        self.assertEqual(out.filename, "1.wav",
                         "Wrong filename in returned GridOut object, expected '1.wav', got '{out.filename}'")

        # file object should contain non-empty bytes
        self.assertGreater(out.length, 0,
                           "Returned GridOut should contain non-empty audio bytes")

    def test_fnc_get_user_mongo_id(self):
        out = self.sm._get_user_mongo_id(self.test_usernames[0])
        self.assertTrue(isinstance(out, ObjectId),
                        f"Expected 'ObjectId' returned but got '{type(out)}'")

        # user which does not exist shoud not have id
        out = self.sm._get_user_mongo_id("Mr Nobody")
        self.assertEqual(out, None, f"Got id for non-existing user")

    def test_fnc_get_file_from_db(self):
        user_1_doc = self.db_collection.find_one(
            {'name': self.test_usernames[0]})
        user_1_sample = user_1_doc["samples"]["train"][0]

        # should return GridOut
        out = self.sm._get_file_from_db(user_1_sample["id"])
        self.assertTrue(isinstance(out, GridOut),
                        f"Expected GridOut returned but got '{type(out)}'")

        # should contain non empty bytes
        self.assertGreater(out.length, 0,
                           "Returned GridOut should contain non-empty audio bytes")

    def test_fnc_get_plot_for_sample(self):
        # check for every possible plot type
        for plot_type in self.sm.ALLOWED_PLOT_TYPES_FROM_SAMPLES:
            out = self.sm.get_plot_for_sample(
                plot_type, "train", self.test_usernames[0], "1.wav")

            # returned value should be instance of tuple
            self.assertTrue(isinstance(out, tuple),
                            f"Expected tuple returned but got '{type(out)}'")
            self.assertTrue(isinstance(out[0], bytes),
                            f"Expected bytes returned but got '{type(out)}'")
            self.assertTrue(isinstance(out[1], str),
                            f"Expected str returned but got '{type(out)}'")

            # should contain nonempty bytes
            self.assertGreater(len(out), 0,
                               "Returned BytesIO should contain non-empty bytes")

        # should throw ValueError for unknown plot type
        args = ["unknown_plot_type", "train", self.test_usernames[0], "1.wav"]
        self.assertRaises(ValueError, self.sm.get_plot_for_sample, *args)

        # should return None if sample, set or username does not exist
        out = self.sm.get_plot_for_sample(
            "mfcc", "train", self.test_usernames[0], "10.wav")
        self.assertEqual(
            out, None, f"Expected returned value to be None but it has type of '{type(out)}'")

    def test_fnc_get_next_filename(self):
        out = self.sm._get_next_filename(self.test_usernames[0], "test")
        self.assertEqual(out, '3.wav',
                         f"Next proper name is '3.wav', got '{out}' instead")

        out = self.sm._get_next_filename(self.test_usernames[0], "train")
        self.assertEqual(out, '4.wav',
                         f"Next proper name is '4.wav', got '{out}' instead")

        out = self.sm._get_next_filename(self.test_usernames[1], "train")
        self.assertEqual(out, '3.wav',
                         f"Next proper name is 1.wav', got '{out}' instead")

        out = self.sm._get_next_filename("Mr Nobody", "train")
        self.assertEqual(out, '1.wav',
                         f"Next proper name is 1.wav', got '{out}' instead")

        out = self.sm._get_next_filename(self.test_usernames[1], "test")
        self.assertEqual(out, '11.wav',
                         f"Next proper name is 11.wav', got '{out}' instead")

    def test_fnc_label_sample_dicts(self):
        user_num = 3
        dicts = [{'id': k} for k in range(5)]
        dicts.extend([{'id': k, 'fake': 'true'} for k in range(5, 10)])
        dicts.extend([{'id': k, 'fake': 'fake'} for k in range(10, 15)])
        res_dicts, labels = self.sm._label_sample_dicts(user_num, dicts, multilabel=True)
        self.assertEqual(len(res_dicts), len(labels),
                         'The number of sample dicts should be the same as labels.'
                         )
        self.assertEqual(res_dicts, dicts[:5] + dicts[10:],
                         'The number of resulting samples should be the same as number of nonfake samples.'
                         )
        self.assertEqual(labels, [user_num] * 10,
                         'If multilabel is true each nonfake sample should be labeled with user_num'
                         )
        res_dicts, labels = self.sm._label_sample_dicts(user_num, dicts, multilabel=False)
        self.assertEqual(len(res_dicts), len(labels),
                         'The number of sample dicts should be the same as labels.'
                         )
        self.assertEqual(res_dicts, dicts,
                         'If multilabel is false, sample_dicts should not be changed.'
                         )
        self.assertEqual(labels, [1] * 5 + [0] * 5 + [1] * 5,
                         'If multilabel is false, each label should be 0/1 depending on "fake" key.'
                         )

    def test_fnc_get_all_samples(self):
        kwargs = {'purpose': 'train', 'multilabel': True, 'sample_type': 'wav'}
        samples, labels = self.sm.get_all_samples(**kwargs)
        self.assertEqual((type(samples), type(labels)), (list, list),
                         'get_all_samples should return a pair of lists if multilabel is tru.e'
                         )
        self.assertEqual(len(samples), len(labels),
                         'The number of samples and labels should be the same.'
                         )
        self.assertEqual(len(self.test_usernames) - 1, max(labels),
                         'The nubmer of usernames and label values should be the same.'
                         )

        for sample in samples:
            self.assertEqual(type(sample), GridOut, 'Each sample should have GridOut type.')
        kwargs.update({'multilabel': False})
        samples, labels = self.sm.get_all_samples(**kwargs)
        self.assertEqual((type(samples), type(labels)), (dict, dict),
                         'get_all_samples should return a pair of dicts if multilabel is false.'
                         )
        self.assertEqual(list(samples.keys()), list(labels.keys()),
                         'The keys of samples should be the same as the keys of labels.'
                         )
        self.assertEqual(list(samples.keys()), self.test_usernames,
                         'There should be a key for each username having a sample.'
                         )
        for name in self.test_usernames:
            self.assertEqual(len(samples[name]), len(labels[name]),
                             'The number of labels should be the same as the number of samples for each user'
                             )
            for label in labels[name]:
                self.assertIn(label, (0, 1),
                              'Each label can be either 0 or 1.'
                              )

    def test_fnc_get_user_tags(self):
        # get and check
        out = self.sm.get_user_tags(self.test_usernames[0])
        self.assertTrue(isinstance(out, dict),
                        f"Expected 'dict' returned but got '{type(out)}'")
        self.assertTrue(out, f"User '{self.test_usernames[0]}' tag list should not be empty")

        out = self.sm.get_user_tags(self.test_usernames[1])
        self.assertFalse(out, f"User '{self.test_usernames[1]}' tag list should be empty")

        # should return empty for no user
        out = self.sm.get_user_tags("Mr Nobody")
        self.assertFalse(out, f"Should return empty dict for non-existing user")

    def test_fnc_get_all_tags(self):
        # get and check
        out = self.sm.get_all_tags()
        self.assertTrue(isinstance(out, list),
                        f"Expected 'list' returned but got '{type(out)}'")
        self.assertEqual(list(self.test_tags.keys()), out,
                         f"Expected list of all tag names, but got {out}")

    def test_fnc_get_tag_values(self):
        # get and check
        test_tag_name = list(self.test_tags.keys())[0]
        test_tag_values = self.test_tags[test_tag_name]

        out = self.sm.get_tag_values(test_tag_name)
        self.assertTrue(isinstance(out, list),
                        f"Expected 'list' returned but got '{type(out)}'")

        self.assertEqual(out, test_tag_values, f"Got unexpected tag values")

        # non-existaing tag
        self.assertRaises(ValueError, self.sm.get_tag_values, "no-tag")

    def test_fnc_tag_exists(self):
        # test both options
        test_tag_name = list(self.test_tags.keys())[0]
        self.assertTrue(self.sm.tag_exists(test_tag_name),
                        "Should return True for existing tag but got False")
        self.assertFalse(self.sm.tag_exists("no-tag"),
                         "Should return False for non-existing tag but got True")

    def test_fnc_user_has_tag(self):
        # test both options
        test_tag_name = list(self.test_tags.keys())[0]
        test_username = self.test_usernames[0]
        self.assertTrue(self.sm.user_has_tag(test_username, test_tag_name),
                        f"Tag '{test_tag_name}' should be present in users' tags but function returned False")
        self.assertFalse(self.sm.user_has_tag(test_username, "no-tag"),
                         f"Tag 'no-tag' should not be present in users' tags but function returned True")

        # non-existing username
        self.assertRaises(ValueError, self.sm.user_has_tag, "Mr Nobody", test_tag_name)

    def test_fnc_get_user_summary(self):
        test_username = self.test_usernames[0]
        expected_fields = ["username", "normalized_username", "created", "tags", "samples"]
        out = self.sm.get_user_summary(test_username)
        fields = list(out.keys())
        self.assertTrue(isinstance(out, dict),
                        f"Expected 'dict' returned but got '{type(out)}'")

        for field in expected_fields:
            self.assertIn(field, fields,
                          f"Could not find field '{field}' to be found in summary")

        out = self.sm.get_user_summary("Mr Nobody")
        self.assertFalse(out, "Expected empty dictionary for non-existing user but got '{out}'")

    def test_fnc_get_tags_summary(self):
        out = self.sm.get_tags_summary()
        self.assertTrue(isinstance(out, dict),
                        f"Expected 'dict' returned but got '{type(out)}'")
        self.assertEqual(len(out.keys()), 2, f"Should return 2 tags but got {len(out.keys())}")
        self.assertEqual(out["gender"], [{'value': 'male', 'count': 1}])


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

        self.assertRaises(UsernameException,
                          self.sm._get_normalized_username, username_special)

    def test_fnc_is_allowed_file_extension(self):
        self.assertTrue(self.sm.is_allowed_file_extension("audio/wav"),
                        "Expected True returned for 'audio/wav'")
        self.assertFalse(self.sm.is_allowed_file_extension("audio/unknown"),
                         "Expected False returned for unknown file extension")

    def test_fnc_get_sample_class_document_template(self):
        out = self.sm._get_sample_class_document_template("user")
        expected_fields = set(
            ['name', 'nameNormalized', 'created', 'samples', 'tags'])

        self.assertEqual(set(out.keys()), expected_fields,
                         f"Expected fields: {expected_fields}, but got {out.keys()}")

    def test_fnc_get_sample_file_document_template(self):
        out = self.sm._get_sample_file_document_template(
            '1.wav', ObjectId('555fc7956cda204928c9dbab'), fake=False)
        expected_fields = set(['id', 'filename', 'recognizedSpeech', 'fake'])

        self.assertEqual(set(out.keys()), expected_fields,
                         f"Expected fields: {expected_fields}, but got {out.keys()}")


if __name__ == '__main__':
    unittest.main()
