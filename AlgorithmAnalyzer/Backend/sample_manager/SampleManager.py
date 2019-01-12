import datetime
import io
import re
import unicodedata
from io import BytesIO
from typing import Tuple, Optional, Dict, List

import gridfs
from werkzeug.utils import secure_filename
from mimetypes import guess_type
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from gridfs import GridOut

from utils import convert_audio
from utils.speech_recognition_wrapper import speech_to_text_wrapper
from plots import mfcc_plot

''''''''''''''''
example of single MongoDB document representing single 'user'

{
    "_id" : ObjectId("5c05b2a837aeab2bca848c74"),      // mongo document id
    "name" : "Test Test",                              // base username, set during new user creation
    "nameNormalized" : "test_test",                   // normalized name, unique for every user
    "created" : ISODate("2018-12-03T22:48:08.449Z"),   // creation timestamp
    "samples" : {                                      // here store samples
        "train" : [
            { "filename" : "1.wav", "id" : ObjectId("5c05b2a837aeab2bca848c75"), recognizedSpeech: "" },  //single sample document
            { "filename" : "2.wav", "id" : ObjectId("5c05b7ae37aeab2f3e779659"), recognizedSpeech: "" }
                  ]
        "test" : [
            { "filename" : "1.wav", "id" : ObjectId("5c05c17c37aeab3cf2e5cb76"), recognizedSpeech: "" },
                 ]
    },
    "tags" : {"gender": "male", "age": "20-29"}        // all user-specific tags
}
'''''''''''''''


class SampleManager:
    # allowed plots' file extensions
    ALLOWED_PLOT_FILE_EXTENSIONS = ['pdf', 'png']
    ALLOWED_PLOT_TYPES_FROM_SAMPLES = ['mfcc']
    ALLOWED_SAMPLE_CONTENT_TYPE = ['audio/wav', 'audio/x-wav']

    def __init__(self, db_url: str, db_name: str, show_logs: bool = True):
        """
        :param db_url: str - url to MongoDB database, it can contain port eg: 'localhost:27017'
        :param db_name: str - database name
        :param show_logs: bool - used to suppress log messages
        """
        # setup MongoDB database connection
        self.db_url = db_url
        self.db_client = MongoClient(db_url, serverSelectionTimeoutMS=5000)
        self.db_database = self.db_client[db_name]
        self.db_collection = self.db_database.samples
        self.db_file_storage = gridfs.GridFS(self.db_database)
        try:
            if show_logs:
                print(f" * #INFO: testing db connection: '{db_url}'...")
            self.db_client.server_info()
        except errors.ServerSelectionTimeoutError as e:
            raise DatabaseException(
                f"Could not connect to MongoDB at '{db_url}'")

        self.show_logs = show_logs

    def is_db_available(self) -> bool:
        """
        check database connection
        """
        try:
            self.db_client.server_info()
            return True
        except errors.AutoReconnect or errors.ServerSelectionTimeoutError:
            return False

    def get_all_usernames(self) -> list:
        """
        get list of all usernames in samplebase
        """
        out = []
        try:
            usernames = self.db_collection.find({}, ["name"])
            for user in usernames:
                out.append(user['name'])
        except errors.PyMongoError as e:
            raise DatabaseException(e)
        return out

    def user_exists(self, username: str) -> bool:
        """
        check if user already exists in samplebas
        :param username: str - eg. 'Hugo Kołątaj'
        """
        norm_name = self._get_normalized_username(username)
        try:
            out = self.db_collection.find_one({"nameNormalized": norm_name})
        except errors.PyMongoError as e:
            raise DatabaseException(e)
        return True if out else False

    def sample_exists(self, username: str, set_type: str, samplename: str) -> bool:
        """
        check if sample exists in samplebase
        :param username: str - eg. 'Hugo Kołątaj'
        :param set_type: str - one of avalible sample classes from config
        :param samplename str - eg. '1.wav'
        """
        sample_list = self.get_user_sample_list(username, set_type)
        return samplename in sample_list

    def create_user(self, username: str) -> ObjectId:
        """
        create new user in samplebase
        check if it does not already exist before creating new document in database
        :param username: str - eg. 'Hugo Kołątaj'
        :returns id: ObjectId - id of freshly added document
        """
        try:
            if(bool(self.db_collection.find_one({"name": username}))):
                raise UsernameException(
                    f"Can't create new user '{username}', it already exists in samplebase")
            new_sample = self._get_sample_class_document_template(username)
            id = self.db_collection.insert_one(new_sample).inserted_id
        except errors.PyMongoError as e:
            raise DatabaseException(e)
        return id

    def get_user_sample_list(self, username: str, set_type: str) -> list:
        """
        get list of files from particular user
        :param username: str - eg. 'Hugo Kołątaj'
        :param set_type: str - one of available sample classes from config
        """
        id = self._get_user_mongo_id(username)
        doc = self.db_collection.find_one(
            {'_id': id}, {f"samples.{set_type}.filename": 1, '_id': 0})
        if not doc:
            return []
        sample_names = []
        for sample in doc['samples'][set_type]:
            sample_names.append(sample['filename'])
        return sample_names

    def save_new_sample(
            self, username: str, set_type: str, file_bytes: bytes,
            content_type: str, fake: bool, recognize=True,
            ) -> Optional[str]:
        """
        saves new sample in samplebase, creates new user if
        it wasn't created yet
        :param username: str - eg. 'Hugo Kołątaj'
        :param set_type: str - one of available sample classes from config
        :param file_bytes: bytes - audio file as bytes
        :param content_type: str - type of provided file, eg: 'audio/wav', 'audio/webm'
        :param recognize: bool - indicates if speech from sample have to be recognized
                                 saved into samplebase and returned
        :returns recognized_speech: Optional[str] - recognized speech from provided audio sample
                                                    if recognized param is set to True
        """
        if not self.user_exists(username):
            self.create_user(username)

        if(self._is_allowed_file_extension(content_type)):
            wav_bytesIO = BytesIO(file_bytes)
        else:
            webm_bytesIO = BytesIO(file_bytes)
            wav_bytesIO = convert_audio.convert_audio_to_format(
                webm_bytesIO,  "wav")

        recognized_speech = None
        if recognize:
            recognized_speech = speech_to_text_wrapper.recognize_speech_from_bytesIO(
                BytesIO(wav_bytesIO.getvalue()))

        try:
            filename = self._get_next_filename(username, set_type)
            user_id = self._get_user_mongo_id(username)
            file_id = self._save_file_to_db(
                filename, file_bytes=wav_bytesIO.read(), content_type=content_type)
            new_file_doc = self._get_sample_file_document_template(
                filename, file_id, fake=fake, rec_speech=recognized_speech)
            self.db_collection.update_one(
                {'_id': user_id}, {'$push': {f'samples.{set_type}': new_file_doc}})
        except errors.PyMongoError as e:
            raise DatabaseException(e)

        return recognized_speech

    def get_plot_for_sample(self, plot_type: str, set_type: str,
                            username: str, sample_name: str,
                            file_extension: str="png", **parameters) -> Tuple[Optional[BytesIO], str]:
        """
        Master method that creates a plot of given plot_type (e.g. "mfcc")
        for a given set_type (train, test), username and specific sample
        file_extension can be specified (png or pdf)

        :param plot_type: str type of plot, e.g. "mfcc"
        :param set_type: set of users' sample, test or train
        :param username: str normalized username of the user
        :param sample_name: str name of the sample, e.g. "1.wav"
        :param file_extension: pdf or png file extension of the plot file
        :param parameters: extra plot type specific parameters, pass as keyworded
        e.g. alfa=10, beta=20
        :return file_name, file_bytes: str mimetype of file,
        BytesIO containing the requested plot
        """
        audio_file_obj = self.get_samplefile(username, set_type, sample_name)
        if audio_file_obj is None:
            return None

        audio_bytes = audio_file_obj.read()
        if plot_type == "mfcc":
            file_io = mfcc_plot.plot_save_mfcc_color_boxes(
                audio_bytes, sample_name, file_extension)
            file_bytes = file_io.getvalue()
        else:
            raise ValueError("plot_type should be of type str, of value one of"
                             f"{self.ALLOWED_PLOT_TYPES_FROM_SAMPLES}")
        content_type, _ = guess_type(f"file.{file_extension}")
        return file_bytes, content_type

    def get_samplefile(self, username: str, set_type: str, samplename: str) -> GridOut:
        """
        retrive sample from database, return as file-like object (with read() method)
        :param username: str - eg. 'Hugo Kołątaj'
        :param set_type: str - one of avalible sample classes from config
        :param samplename: str - eg. '1.wav'
        :returns fileObj: GridOut - file-like object with read() method,
                                    it contains content_type and file_name
        """
        user_id = self._get_user_mongo_id(username)

        # aggregation query to find file id
        aggregation_pipeline = [
            {'$match': {'_id': user_id}},
            {'$project': {f"samples.{set_type}": 1, '_id': 0}},
            {'$unwind': f"$samples.{set_type}"},
            {'$match': {f"samples.{set_type}.filename": samplename}},
            {'$project': {"id": f"$samples.{set_type}.id"}}
        ]
        try:
            temp_doc = list(self.db_collection.aggregate(aggregation_pipeline))
            if not temp_doc:
                return None
            id = list(temp_doc)[0]['id']
            fileObj = self.db_file_storage.get(id)
        except errors.PyMongoError as e:
            raise DatabaseException(e)
        return fileObj

    # def _is_username_valid(self, username: str) -> bool:
    #     """
    #     check if given username is valid
    #     """
    #     return not re.match('^\w+$', username)

    def _is_allowed_file_extension(self, file_type: str) -> bool:
        """
        checks whether mimetype of the file is allowed
        :param file_type: str
        :return: True/False
        """
        return True if file_type in self.ALLOWED_SAMPLE_CONTENT_TYPE else False

    # def _create_plot_mfcc_for_sample(self, audio_bytes,
    #                                  file_extension: str = "png") -> bytes:
    #     """
    #     This creates a MFCC plot file of file_extension file (pdf or png)
    #     for the audio_path file given.
    #     The plot is saved in the user+type dirpath.

    #     :param audio_path: str full path to the sample file
    #     :param directory_path: str full path to the sample's directory,
    #     e.g username/ or username/set_type
    #     :param file_extension: pdf or png file extension of the plot mfcc file
    #     :return file_path, file_io: str file_path to the saved file,
    #     BytesIO containing the requested plot
    #     """
    #     # TODO: Not unit tested!
    #     file_io = mfcc_plot.plot_save_mfcc_color_boxes(audio_bytes, file_name, file_extension)

    #     return file_path, file_io.getvalue()

    def _get_plot_for_sample_file(self, audio_path: str, plot_type: str,
                                  file_extension: str = "png") -> Tuple[str, bytes]:
        """
        This helper gets str plot's path and plot's content as BytesIO
        based on str audio_path of the
        with a file_extension given (or None for png)
        already exists

        :param audio_path: str full path to the sample file
        :param plot_type: str type of plot, e.g. "mfcc"
        :param file_extension: pdf or png file extension of the plot mfcc file
        :raises FileNotFoundError:
        :return: str path to the plot, and BytesIO plot's contents
        """
        # TODO: This will have to be remade once a new SampleManager rolls out
        # TODO: NOT UNIT TESTED AWAITING FOR CHANGE
        expected_plot_path = f"{self._get_sample_file_name_from_path(audio_path)}_{plot_type.lower()}.{file_extension.lower()}"
        with open(expected_plot_path, mode='rb') as plot_file:
            return expected_plot_path, io.BytesIO(plot_file.read()).getvalue()

    def _get_normalized_username(self, username: str) -> str:
        """
        Normalize username, which could include spaces,
        big letters and diacritical marks
        example: 'Hugo Kołątaj' --> 'hugo_kolataj'
        :param username: str - eg. 'Hugo Kołątaj'
        """
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
        temp = unicodedata.normalize('NFKD', temp).encode(
            'ascii', 'ignore').decode('ascii')
        if not re.match('^\w+$', temp):
            raise UsernameException(
                'Incorrect username "{}" !'.format(temp)
            )
        return secure_filename(temp)

    def _get_sample_class_document_template(self, username: str) -> dict:
        """
        get single sample class document template, needed when there is
        need for 'fresh' document templete, eg. creating new user
        """
        return {"name": username,
                "nameNormalized": self._get_normalized_username(username),
                "created": datetime.datetime.utcnow(),
                "samples": {"train": [], "test": []},
                "tags": []
                }

    def _get_sample_file_document_template(
            self, filename: str, id: ObjectId, fake: bool, rec_speech: str = ""
            ) -> dict:
        """
        get single file document template
        """
        return {"filename": filename, "id": id, "fake": fake, "recognizedSpeech": rec_speech}

    def _get_user_mongo_id(self, username: str) -> ObjectId:
        """
        needed when we want to refer to db document via mongo _id
        and have username
        """
        try:
            doc = self.db_collection.find_one(
                {"nameNormalized": self._get_normalized_username(username)})
        except errors.PyMongoError as e:
            raise DatabaseException(e)
        return doc['_id'] if doc else None

    def _save_file_to_db(self, filename: str, file_bytes=None, content_type: str = None):
        """
        save file-like object, eg. FileStorage or BytesIO, to database
        """
        if content_type is None:
            content_type, _ = guess_type(filename)

        storage = self.db_file_storage
        try:
            id = storage.put(file_bytes, filename=filename,
                             content_type=content_type)
        except errors.PyMongoError as e:
            raise DatabaseException(e)

        return id

    def _get_file_from_db(self, id: ObjectId):
        """
        get file-like object from database
        """
        storage = self.db_file_storage
        try:
            fileObj = storage.get(id)
        except errors.PyMongoError as e:
            raise DatabaseException(e)

        return fileObj

    def _get_next_filename(self, username: str, set_type: str) -> str:
        """
        get next valid name for new file
        eg. if user has files '1.wav', '2.wav' in samplebase it will return '3.wav'

        :param username:str - eg. 'Stanisław Gołębiewski'
        :param set_type:str - 'test' or 'train'
        """
        all_files = self.get_user_sample_list(username, set_type)
        if not all_files:
            return '1.wav'
        all_filenames = self.get_user_sample_list(username, set_type)
        all_filenames_numbers = []
        for filename in all_filenames:
            regex = re.match('(.+)\.(.+$)', filename)
            if not regex or not regex.group(1).isdigit():
                raise ValueError(
                    f"Invalid filename retrived from database: {filename}, should be: '<number>.wav'")

            all_filenames_numbers.append(int(regex.group(1)))
        last_file = max(all_filenames_numbers)
        next_number = last_file + 1
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

    def _label_sample_dicts(self, user_num, sample_dicts, multilabel: bool) -> Tuple[List[dict], List[int]]:
        """
        Creates labels for samples and filters samples. If `multilabel` is false,
        labels each sample 0 / 1 depending on 'fake' key associated with sample.
        If `multilabel` is true, returns only real samples (there is no 'fake' key or is false)
        and labels each with `user_num`.
        :param user_num: The user number
        :param sample_dicts: all dicts associated with user's samples
        :param multilabel: if false, labels will be 0/1 depending on sample being fake,
        else `user_num` will be used to labelthe samples
        :returns: list of filterd sample dicts and their labels
        """
        if multilabel:
            sample_dicts = [
                sample_dict for sample_dict in sample_dicts
                if not ('fake' in sample_dict and sample_dict['fake'] == 'true')
            ]
            labels = [user_num] * len(sample_dicts)
        else:
            labels = [
                1 - ('fake' in sample_dict and sample_dict['fake'] == 'true') for sample_dict in sample_dicts
            ]
        return sample_dicts, labels

    def get_all_samples(self, purpose: str, multilabel: bool, sample_type: str) -> tuple:
        """
        Get all samples from the database.
        :param purpose: either "train" for training samples or "test" for testing
        :param multilabel: true for multilabel algorithms, false for yes/no models
        :returns: If multilabel is false, returns two dicts:
            {'username': [samplelist]}, {'username': [0/1 label list (real/fake)]}.
        If multilabel is true, returns two lists
            [sample_list], [label_list],
        each label is the user's number (int) and won't change after the user is created.
        """
        # TODO(mikra): return a generator object instead of list (memory efficiency)
        if multilabel:
            samples, labels = [], []
        else:
            samples, labels = {}, {}
        user_docs = self.db_collection.find({}).sort('id', 1)
        # ^this effectively sorts all docs by timestamp created,
        # so each user will have the same number each time
        for num, user_doc in enumerate(user_docs):
            if not user_doc or 'samples' not in user_doc:
                continue
            username = user_doc['name']
            user_samples = user_doc['samples'][purpose] if purpose in user_doc['samples'] else []
            user_samples, user_labels = self._label_sample_dicts(num, user_samples, multilabel)
            if multilabel:
                samples.extend([self._get_file_from_db(sample['id']) for sample in user_samples])
                labels.extend(user_labels)
            else:
                samples[username] = [self._get_file_from_db(sample['id']) for sample in user_samples]
                labels[username] = user_labels
        return samples, labels


class UsernameException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class DatabaseException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        # self.__str__ = mongo_error.__str__
