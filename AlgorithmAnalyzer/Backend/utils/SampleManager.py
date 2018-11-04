import os
import re
import unicodedata
import json
import typing

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from scipy.io import wavfile
from pathlib import Path

from convert_audio_wrapper import convert_webm
from speech_recognition_wrapper import speech_to_text_wrapper

''''''''''''''''
example of directory structure

data/    <---- root directory
├── hugo_kolataj
│   ├── 1.json
│   ├── 1.wav   <----- sample from 'train' set
│   └── test
│       ├── 1.json
│       ├── 1.wav
│       ├── 2.json
│       ├── 2.wav    <----- sample from 'test' set
│       ├── 3.json
│       └── 3.wav
└── stanislaw_golebiewski  <---- username / user directory
    ├── 1.json
    ├── 1.wav
    ├── 2.json
    ├── 2.wav
    ├── 3.json
    ├── 3.wav
    └── test   <---- test set directory
        ├── 1.json
        ├── 1.wav
        ├── 2.json    <---- json file associated with sample '2.wav'
        └── 2.wav

'''''''''''''''


class UsernameException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class SampleManager:
    def __init__(self, path):
        '''path:  string or path; path to root directory'''

        self.path = os.path.normpath(path)

    def _mkdir(self, name):
        if self._user_directory_exists(name):
            return
        os.makedirs(os.path.join(self.path, name))

    def get_all_usernames(self):
        d = []
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            d.extend(dirnames)
            break
        return d

    def _user_directory_exists(self, dirname):
        return os.path.isdir(os.path.join(self.path, dirname))

    def user_exists(self, username):
        user = self.username_to_dirname(username)
        return self._user_directory_exists(user)

    def file_exists(self, username, type, sample):
        dir = self.get_user_dirpath(username)
        if type == 'test':
            dir = os.path.join(dir, type)
        return Path(os.path.join(dir, sample)).exists()

    def create_user(self, username):
        user = self.username_to_dirname(username)
        self._mkdir(user)
        self._mkdir(os.path.join(user, 'test'))

    def get_samples(self, username, set_type='train'):
        user = self.username_to_dirname(username)
        samples = []
        if set_type == 'train':
            samples = list(os.listdir(os.path.join(self.path, user)))
            samples.remove('test')
        else:
            samples = list(os.listdir(os.path.join(self.path, user, 'test')))
        rgx = re.compile('.+\.wav$')
        return list(filter(rgx.match, samples))

    def get_new_sample_path(self, username, set_type="train", filetype="wav", no_file_type=False):
        samples = self.get_samples(username, set_type)
        username = self.username_to_dirname(username)

        if samples:
            last_sample = max(
                int(name.split('.')[0]) for name in samples
            )
        else:
            last_sample = 0
        out_path = os.path.join(self.path, username)
        if set_type == 'test':
            out_path = os.path.join(out_path, set_type)

        if not no_file_type:
            return os.path.join(out_path, str(last_sample + 1) + '.' + filetype)
        else:
            return os.path.join(out_path, str(last_sample + 1))

    def get_user_dirpath(self, username, type='train'):
        if type == 'train':
            return os.path.join(self.path, self.username_to_dirname(username))
        else:
            return os.path.join(self.path, type,  self.username_to_dirname(username))

    @staticmethod
    def get_new_json_path(audio_path: str) -> str:
        """ this gets path for a new recording's json file
         based on str audio_path
         e.g C:/aasda/a.wav -> C:/aasda/a.json"""
        return audio_path.rsplit('.', 1)[0]+".json"

    def add_sample(self, username, sample):
        '''
            this method serves to save samples
            for now it's not used
        '''
        new_path = self.get_new_sample_path(username)
        with open(new_path, 'wb') as new:
            new.write(sample)

    def get_sample(self, username, sample_number):
        username = self.username_to_dirname(username)
        sample_path = os.path.join(
            self.path, username,
            '{}.wav'.format(sample_number)
        )
        return wavfile.read(sample_path)

    def _invalid_username(self, username):
        return not re.match('^\w+$', username)

    # def save_new_sample(self, username: str, file: FileStorage, type: str) -> str:
    #     if not self.user_exists(username):
    #         self.create_user(username)
    #     path = self.get_new_sample_path(username, set_type=type, filetype="webm")
    #     file.save(path)
    #     return path

    @staticmethod
    def is_allowed_file_extension(file: FileStorage) -> bool:
        """
        checks whether mimetype of the file is allowed
        :param file: FileStorage
        :return: True/False
        """
        return True if file.mimetype == "audio/wav" else False

    def save_new_sample(self, username: str, file: FileStorage, set_type: str) -> typing.Tuple[str, str]:
        """
        saves new sample as both .webm and wav with a JSON file
        :param username: str
        :param file: FileStorage
        :return: str wav_path, str recognized_speech
        """
        if not self.user_exists(username):
            self.create_user(username)

        if self.is_allowed_file_extension(file):
            wav_path = self.get_new_sample_path(username, set_type=set_type, filetype="wav")
            file.save(wav_path)
            print(f"#LOG {self.__class__.__name__}: .wav file saved to: " + wav_path)
        else:
            # not-wav file is temporarily saved
            temp_path = self.get_new_sample_path(username, set_type=set_type, no_file_type=True)
            print()
            file.save(temp_path)

            # convert to webm
            wav_path = convert_webm.convert_webm_to_format(
                temp_path, temp_path,  "wav")
            print("#LOG {self.__class__.__name__}: .wav file converted and saved to: " + wav_path)

            # delete temp file
            os.remove(temp_path)

        # recognize speech
        recognized_speech = speech_to_text_wrapper.recognize_speech_from_path(wav_path)
        print(f"#LOG {self.__class__.__name__}: Recognized words: {recognized_speech}")

        # save the new sample json
        json_path = self.create_a_new_sample_properties_json(username, audio_path=wav_path,
                                                             data={"recognized_speech": recognized_speech})
        print(f"#LOG {self.__class__.__name__}: Created a JSON file: {json_path}")

        return wav_path, recognized_speech

    @staticmethod
    def create_a_new_sample_properties_json(username, data: typing.Dict[str, str], audio_path: str) -> str:
        """
        this creates a json file for the newest sample for the username given
        e.g: 5.json
        takes data to be saved in the form of dict[string, string]
        audio_path is a path to the audio file to be accompanied by json file
        :param username: str
        :param data: typing.Dict[str, str]
        :param audio_path: str path to audio
        :return: str path to json
        """
        json_path = SampleManager.get_new_json_path(audio_path)
        with open(json_path, 'w', encoding='utf8') as json_file:
            recording_properties = {"name": username, **data}
            string_json = str(json.dumps(recording_properties, ensure_ascii=False).encode('utf8'), encoding='utf8')
            json_file.writelines(string_json)
        return json_path

    def is_wav_file(self, samplename):
        return re.match('.+\.wav$', samplename)

    def username_to_dirname(self, username: str):
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

    def file_has_proper_extension(self, filename: str, allowed_extensions: list) -> typing.Tuple[bool, str]:
        """
        it takes 'filename' and decide if it has extension which can be found
        in 'allowed_extensions'
      
        important: extensions in 'allowed_extensions' should not start with dot, eg:
           good: ['webm', 'cat', 'wav']
           bad:  ['.webm', '.cat', '.wav']
        """
        # regular expression for files with extensions (file).(extension)
        regex = re.match('(.+)\.(.+$)', filename)
        if not regex:
            return False, ""
        else:
            file_extension = regex.group(2)
            if file_extension not in allowed_extensions:
                return False, file_extension
            else:
                return True, file_extension
