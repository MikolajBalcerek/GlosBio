import re
import unicodedata
import gridfs
import datetime

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from mimetypes import guess_type
from pymongo import MongoClient, errors
from bson.objectid import ObjectId

# from utils import convert_webm
# from utils.speech_recognition_wrapper import speech_to_text_wrapper

''''''''''''''''
example of single MongoDB document representing single 'user'

{
    "_id" : ObjectId("5c05b2a837aeab2bca848c74"),      // mongo document id
    "name" : "Test Test",                              // base username, set during new user creation
    "nameNormalized" : "test_test",                   // normalized name, unique for every user
    "created" : ISODate("2018-12-03T22:48:08.449Z"),   // creation timestamp
    "samples" : {                                      // here store samples
        "train" : [
            { "filename" : "1.wav", "id" : ObjectId("5c05b2a837aeab2bca848c75") },  //single sample document
            { "filename" : "2.wav", "id" : ObjectId("5c05b7ae37aeab2f3e779659") }
                  ]
        "test" : [
            { "filename" : "1.wav", "id" : ObjectId("5c05c17c37aeab3cf2e5cb76") },
                 ]
    },
    "tags" : {"gender": "male", "age": "20-29"}        // all user-specific tags
}
'''''''''''''''


class SampleManager:
    def __init__(self, db_url: str, db_name: str, show_logs: bool = True):
        '''
        :param db_url: str - url to MongioDB database, it can contain port eg: "localhost:27017"
        :param db_name: str - database name
        :param testing: bool - used to suppress log messages
        '''
        # setup MongoDB database connetion
        self.db_client = MongoClient(db_url)
        self.db_database = self.db_client[db_name]
        self.db_collection = self.db_database.samples
        self.db_file_storage = gridfs.GridFS(self.db_database)
        try:
            if show_logs:
                print(f" * #INFO: testing db connection: '{db_url}'...")
            self.db_client.server_info()
        except errors.ServerSelectionTimeoutError:
            raise Exception("Could not connect to MongoDB database...")

        self.show_logs = show_logs

    def get_all_usernames(self) -> list:
        '''
        get list of all usernames in samplebase
        '''
        out = []
        try:
            usernames = self.db_collection.find({}, ["name"])
            for user in usernames:
                out.append(user['name'])
        except Exception:
            raise
        return out

    def user_exists(self, username: str) -> bool:
        '''
        check if user already exists in samplebas
        :param username: str - eg. "Hugo Kołątaj"
        '''
        norm_name = self._get_normalized_username(username)
        return True if self.db_collection.find_one({"nameNormalized": norm_name}) else False

    def sample_exists(self, username: str, set_type: str, samplename: str) -> bool:
        '''
        check if sample exists in samplebase
        :param username: str - eg. "Hugo Kołątaj"
        :param set_type: str - one of avalible sample classes from config
        :param samplename str - eg. "1.wav"
        '''
        sample_list = self.get_user_sample_list(username, set_type)
        return samplename in sample_list

    def create_user(self, username: str) -> ObjectId:
        '''
        create new user in samplebase
        :param username: str - eg. "Hugo Kołątaj"
        '''
        new_saple = self._get_sample_class_document_template(username)
        id = self.db_collection.insert_one(new_saple).inserted_id
        return id

    def get_user_sample_list(self, username: str, set_type: str) -> list:
        '''
        get list of files from particular user
        :param username: str - eg. "Hugo Kołątaj"
        :param set_type: str - one of avalible sample classes from config
        '''
        id = self._get_user_mongo_id(username)
        doc = self.db_collection.find_one({'_id': id}, {f"samples.{set_type}.filename": 1, '_id': 0})
        if not doc['samples']:
            return []
        sample_names = []
        for sample in doc['samples'][set_type]:
            sample_names.append(sample['filename'])
        return sample_names

    def save_new_sample(self, username: str, set_type: str, file: FileStorage) -> str:
        '''
        saves new sample in samplebase, creates new user if
        it wasn't created yet
        :param username: str - eg. "Hugo Kołątaj"
        :param set_type: str - one of avalible sample classes from config
        :param file: FileStorage
        '''
        # TO DO: add speech to text
        if not self.user_exists(username):
            self.create_user(username)

        try:
            filename = self._get_next_filename(username, set_type)
            user_id = self._get_user_mongo_id(username)
            file_id = self._save_file_to_db(filename, fileObj=file)
            new_file_doc = self._get_sample_file_document_template(filename, file_id)

            self.db_collection.update_one({'_id': user_id}, {'$push': {f'samples.{set_type}': new_file_doc}})
        except Exception:
            raise

        return ""

    def get_samplefile(self, username: str, set_type: str, samplename: str):
        '''
        retrive sample from database, return as file-like object (with read() method)
        :param username: str - eg. "Hugo Kołątaj"
        :param set_type: str - one of avalible sample classes from config
        :param samplename str - eg. "1.wav"
        '''
        user_id = self._get_user_mongo_id(username)

        # aggregation query to find file id
        aggregation_pipeline = [
            {'$match': {'_id': user_id}},
            {'$project': {f"samples.{set_type}": 1, '_id': 0}},
            {'$unwind': f"$samples.{set_type}"},
            {'$match': {f"samples.{set_type}.filename": samplename}},
            {'$project': {"id": f"$samples.{set_type}.id"}}
            ]

        temp_doc = list(self.db_collection.aggregate(aggregation_pipeline))
        if not temp_doc:
            return None
        id = list(temp_doc)[0]['id']
        fileObj = self.db_file_storage.get(id)
        return fileObj

    def _invalid_username(self, username: str) -> bool:
        '''
        check if given username is valid
        '''
        return not re.match('^\w+$', username)

    def _get_normalized_username(self, username: str) -> str:
        '''
        Normalize username, which could include spaces,
        big letters and diacritical marks
        example: "Hugo Kołątaj" --> "hugo_kolataj"
        :param username: str - eg. "Hugo Kołątaj"
        '''

        temp = username.lower()
        d = {
            "ą": "a",
            "ć": "c",
            "ę": "e",
            "ł": "l",
            "ó": "o",
            "ś": "s",
            "ź": "z",
            "ż": "z"
        }
        for diac, normal in d.items():
            temp = temp.replace(diac, normal)
        temp = temp.replace(" ", "_")
        temp = unicodedata.normalize('NFKD', temp).encode('ascii', 'ignore').decode('ascii')
        if self._invalid_username(temp):
            raise UsernameException(
                'Incorrect username "{}" !'.format(temp)
            )
        return secure_filename(temp)

    def _get_sample_class_document_template(self, username: str ="No Name") -> dict:
        '''
        get single sample class document template, needed when there is
        need for 'fresh' document templete, eg. creating new user
        '''
        return {"name": username,
                "nameNormalized": self._get_normalized_username(username),
                "created": datetime.datetime.utcnow(),
                "samples": {"train": [], "test": []},
                "tags": []
                }

    def _get_sample_file_document_template(self, filename, id: ObjectId) -> dict:
        '''
        get single file document template
        '''
        return {"filename": filename, "id": id, "recognizedSpeech": ""}

    def _get_user_mongo_id(self, username: str) -> ObjectId:
        '''
        needed when we want to refere to db document via mongo _id
        and have username
        '''
        doc = self.db_collection.find_one({"nameNormalized": self._get_normalized_username(username)})
        return doc['_id'] if doc else None

    def _save_file_to_db(self, filename: str, fileObj=None, content_type: str = None):
        '''
        save file-like object, eg. FileStorage, to database
        '''
        if content_type is None:
            content_type, _ = guess_type(filename)

        storage = self.db_file_storage
        id = storage.put(fileObj, filename=filename, content_type=content_type)
        return id

    def _get_file_from_db(self, id: ObjectId):
        '''
        get file-like object from database
        '''
        storage = self.db_file_storage
        try:
            fileObj = storage.get(id)
        except Exception:
            raise
        return fileObj

    def _get_next_filename(self, username: str, set_type: str) -> str:
        '''
        get next valid name for new file
        eg. if user has files '1.wav', '2.wav' in samplebase it will return '3.wav'

        :param username:str - eg. 'Stanisław Gołębiewski'
        :param set_type:str - 'test' or 'train'
        '''
        all_files = self.get_user_sample_list(username, set_type)
        if not all_files:
            return '1.wav'
        last_file = max(self.get_user_sample_list(username, set_type))
        regex = re.match('(.+)\.(.+$)', last_file)
        if not regex or not regex.group(1).isdigit():
            raise ValueError(f"Invalid filename retrived from database: {last_file}, should be: '<number>.wav'")
        next_number = int(regex.group(1)) + 1
        return f"{next_number}.wav"

    def _is_wav_file(self, samplename):
        return re.match('.+\.wav$', samplename)

    # def file_has_proper_extension(self, filename: str, allowed_extensions: list) -> typing.Tuple[bool, str]:
    #     """
    #     it takes 'filename' and decide if it has extension which can be found
    #     in 'allowed_extensions'
    #     important: extensions in 'allowed_extensions' should not start with dot, eg:
    #        good: ['webm', 'cat', 'wav']
    #        bad:  ['.webm', '.cat', '.wav']
    #     """
    #     # regular expression for files with extensions (file).(extension)
    #     regex = re.match('(.+)\.(.+$)', filename)
    #     if not regex:
    #         return False, ""
    #     else:
    #         file_extension = regex.group(2)
    #         if file_extension not in allowed_extensions:
    #             return False, file_extension
    #         else:
    #             return True, file_extension


class UsernameException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
