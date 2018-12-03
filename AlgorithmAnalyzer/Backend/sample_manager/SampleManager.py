import os
import sys
import re
import unicodedata
import json
import typing
import pprint

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from mimetypes import guess_type

# from scipy.io import wavfile
# from pathlib import Path
from pymongo import MongoClient, errors
import gridfs
import datetime

from utils import convert_webm
from utils.speech_recognition_wrapper import speech_to_text_wrapper


''''''''''''''''
example of single MongoDB document representing single sample class

{


}

'''''''''''''''


class SampleManager:
    def __init__(self, db_url: str, db_name: str):
        '''
        setup MongoDB database connetion

        :param db_url: url to MongioDB database
        :param db_name: database name
        '''

        self.db_client = MongoClient(db_url)
        self.db_database = self.db_client[db_name]
        self.db_collection = self.db_database.samples
        self.db_file_storage = gridfs.GridFS(self.db_database)
        try:
            print(f" * #INFO: testing db connection: '{db_url}'...")
            self.db_client.server_info()
        except errors.ServerSelectionTimeoutError:
            raise Exception("Could not connect to MongoDB database...")

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
        check if user already exists in samplebase
        '''
        norm_name = self._username_to_dirname(username)
        return True if self.db_collection.find_one({"name-normalized": norm_name}) else False

    def sample_exists(self, username, type, samplename):
        # TO DO: reimplement
        pass
        # dir = self.get_user_dirpath(username)
        # if type == 'test':
        #     dir = os.path.join(dir, type)
        # return Path(os.path.join(dir, sample)).exists()

    def create_user(self, username: str):
        '''
        create new user in samplebase
        '''
        new_saple = self._get_sample_class_document_template(username)
        id = self.db_collection.insert_one(new_saple).inserted_id
        return id

    def get_user_sample_list(self, username: str, set_type: str) -> list:
        '''
        get list of files from particular user
        :param username: str
        :param set_type: str - 'train' or 'test'
        '''
        id = self._get_user_mongo_id(username)
        doc = self.db_collection.find_one({'_id': id}, {f"samples.{set_type}.filename": 1, '_id': 0})
        print(doc['samples'])
        if not doc['samples']:
            return []
        sample_names = []
        for sample in doc['samples'][set_type]:
            sample_names.append(sample['filename'])
        return sample_names

    # @staticmethod
    # def get_new_json_path(audio_path: str) -> str:
    #     """ this gets path for a new recording's json file
    #      based on str audio_path
    #      e.g C:/aasda/a.wav -> C:/aasda/a.json"""
    #     return audio_path.rsplit('.', 1)[0]+".json"

    # def get_sample_file(self, username, type, sample):
        # pass
        # username = self.username_to_dirname(username)
        # sample_path = os.path.join(
        #     self.path, username,
        #     '{}.wav'.format(sample_number)
        # )
        # return wavfile.read(sample_path)

    # @staticmethod
    # def is_allowed_file_extension(file: FileStorage) -> bool:
    #     """
    #     checks whether mimetype of the file is allowed
    #     :param file: FileStorage
    #     :return: True/False
    #     """
    #     return True if file.mimetype == "audio/wav" else False

    def save_new_sample(self, username: str, set_type: str, file: FileStorage) -> str:
        '''

        '''

        if not self.user_exists(username):
            self.create_user(username)

        try:
            file_id = self._save_file_to_db(fileObj=file)
            user_id = self._get_user_mongo_id(username)

            filename = self._get_next_filename(username, set_type)
            new_file_doc = self._get_sample_file_document_template(filename, file_id)

            self.db_collection.update_one({'_id': user_id}, {'$push': {f'samples.{set_type}': new_file_doc}})
        except Exception:
            raise

        return ""

    def get_samplefile(self, username: str, type: str, filename: str):
        '''

        '''
        id = self.db_collection.find_one({'_id': self._get_user_mongo_id(username)}, ["samples.train"])["samples"]["train"][0]
        out = self.db_file_storage.get(id)
        print(out.read())
        out_2 = FileStorage(stream=out.read(), filename="1.wav", content_type="audio/wav")
        return out_2
        
        # if not self.user_exists(username):
        #     self.create_user(username)

        # if self.is_allowed_file_extension(file):
        #     wav_path = self.get_new_sample_path(username, set_type=set_type, filetype="wav")
        #     file.save(wav_path)
        #     print(f"#LOG {self.__class__.__name__}: .wav file saved to: " + wav_path)
        # else:
        #     # not-wav file is temporarily saved
        #     temp_path = self.get_new_sample_path(username, set_type=set_type, no_file_type=True)
        #     print()
        #     file.save(temp_path)

        #     # convert to webm
        #     wav_path = convert_webm.convert_webm_to_format(
        #         temp_path, temp_path,  "wav")
        #     print("#LOG {self.__class__.__name__}: .wav file converted and saved to: " + wav_path)

        #     # delete temp file
        #     os.remove(temp_path)

        # # recognize speech
        # recognized_speech = speech_to_text_wrapper.recognize_speech_from_path(wav_path)
        # print(f"#LOG {self.__class__.__name__}: Recognized words: {recognized_speech}")

        # # save the new sample json
        # json_path = self.create_a_new_sample_properties_json(username, audio_path=wav_path,
        #                                                      data={"recognized_speech": recognized_speech})
        # print(f"#LOG {self.__class__.__name__}: Created a JSON file: {json_path}")

        # return wav_path, recognized_speech

    # @staticmethod
    # def create_a_new_sample_properties_json(username, data: typing.Dict[str, str], audio_path: str) -> str:
    #     """
    #     this creates a json file for the newest sample for the username given
    #     e.g: 5.json
    #     takes data to be saved in the form of dict[string, string]
    #     audio_path is a path to the audio file to be accompanied by json file
    #     :param username: str
    #     :param data: typing.Dict[str, str]
    #     :param audio_path: str path to audio
    #     :return: str path to json
    #     """
    #     json_path = SampleManager.get_new_json_path(audio_path)
    #     with open(json_path, 'w', encoding='utf8') as json_file:
    #         recording_properties = {"name": username, **data}
    #         string_json = str(json.dumps(recording_properties, ensure_ascii=False).encode('utf8'), encoding='utf8')
    #         json_file.writelines(string_json)
    #     return json_path

    # def is_wav_file(self, samplename):
    #     return re.match('.+\.wav$', samplename)
    def _invalid_username(self, username: str) -> bool:
        '''
        check if given username is valid
        '''
        return not re.match('^\w+$', username)
    
    def _username_to_dirname(self, username: str) -> str:
        '''
        Convert username, which could include spaces,
        big letters and diacritical marks, to valid directory name
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
                "name-normalized": self._username_to_dirname(username),
                "created": datetime.datetime.utcnow(),
                "samples": {"train": [], "test": []},
                "tags": []
                }

    def _get_sample_file_document_template(self, filename, id) -> dict:
        '''
        get single file document template
        '''
        return {"filename": filename, "id": id}

    def _get_user_mongo_id(self, username: str):
        '''
        needed when we want to refere to db document via mongo _id
        and have username
        '''
        doc = self.db_collection.find_one({"name-normalized": self._username_to_dirname(username)})
        return doc['_id'] if doc else None

    def _save_file_to_db(self, filename: str = 'test.wav', fileObj=None, content_type: str = None):
        '''
        save file-like object, eg. FileStorage, to database
        '''
        if content_type is None:
            content_type, _ = guess_type(filename)

        storage = self.db_file_storage
        id = storage.put(fileObj, filename=filename, content_type=content_type)
        return id

    def _get_file_from_db(self, id):
        '''
        get file-like object, eg. FileStorage, from database
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
        last_file = max(self.get_user_sample_list(username, set_type))
        if not last_file:
            return '1.wav'
        regex = re.match('(.+)\.(.+$)', last_file)
        if not regex or not regex.group(1).isdigit():
            raise ValueError(f"Invalid filename retrived from database: {last_file}, should be: '<number>.wav'")
        next_number = int(regex.group(1)) + 1
        return f"{next_number}.wav"


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

