import os
import re
import unicodedata
import json
import typing

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from scipy.io import wavfile

from Backend.convert_audio_wrapper import convert_webm
from Backend.speech_recognition_wrapper import speech_to_text_wrapper

''''''''''''''''
#to jest na razie propozycja, jeśli taka struktura nie zagra to będzie trzeba zmienić

example of directory structure

../data/  <----- 'root' directory
│  
├── hugo_kolataj
│   ├── 1.wav
│   └── 2.wav
├── stanislaw_august_poniatowski  <------- username
│   ├── 1.wav
│   ├── 2.wav
│   ├── 3.wav  <-------- audio sample
│   ├── 4.wav
│   └── 5.wav
└── stanislaw_golebiewski
    ├── 1.wav
    ├── 2.wav
    └── 3.wav
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

    def create_user(self, username):
        user = self.username_to_dirname(username)
        self._mkdir(user)

    def get_samples(self, username):
        user = self.username_to_dirname(username)
        return list(os.listdir(os.path.join(self.path, user)))

    def get_new_sample_path(self, username, filetype="wav"):
        samples = self.get_samples(username)
        username = self.username_to_dirname(username)
        if samples:
            last_sample = max(
                int(name.split('.')[0]) for name in samples
            )
        else:
            last_sample = 0
        return os.path.join(self.path, username, str(last_sample + 1) + '.' + filetype)

    @staticmethod
    def get_new_json_path(audio_path : str) -> str:
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

    @staticmethod
    def is_allowed_file(file: FileStorage) -> bool:
        """
        checks whether mimetype of the file is allowed
        :param file: FileStorage
        :return: True/False
        """
        if file.mimetype == "audio/wav":
            return True
        # elif file.mimetype == "video/webm" or file.mimetype == "audio/webm":
        #     print("mimetype wav")
        #     return False
        return False

    def save_new_sample(self, username: str, file: FileStorage) -> typing.Tuple[str, str]:
        """
        saves new sample as both .webm and wav with a JSON file
        :param username: str
        :param file: FileStorage
        :return: str wav_path, str recognized_speech
        """
        if not self.user_exists(username):
            self.create_user(username)

        if self.is_allowed_file(file):
            wav_path = self.get_new_sample_path(username, filetype="wav")
            file.save(wav_path)
            print("#LOG: .wav file saved to: " + wav_path)
        else:
            # not-wav file is temporarily saved
            temp_path = self.get_new_sample_path(username, filetype="")
            file.save(temp_path)

            # convert to webm
            convert_webm.convert_webm_to_format(
                temp_path, temp_path,  "wav")
            wav_path = temp_path +".wav"
            print("#LOG: .wav file converted and saved to: " + wav_path)

            # delete temp file
            os.remove(temp_path)

        # recognize speech
        recognized_speech = speech_to_text_wrapper.recognize_speech_from_path(wav_path)
        print(f"#LOG Recognized words: {recognized_speech}")

        # save the new sample json
        json_path = self.create_a_new_sample_properties_json(username, audio_path=wav_path, data={"recognized_speech": recognized_speech})
        print(f"#LOG Created a JSON file: {json_path}")

        return wav_path, recognized_speech

    @staticmethod
    def create_a_new_sample_properties_json(username, data: typing.Dict[str, str], audio_path : str) -> str:
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
