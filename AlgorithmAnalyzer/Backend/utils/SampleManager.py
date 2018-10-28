import os
import re
import unicodedata
import json
import typing
from random import shuffle
import wave

import numpy as np
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from scipy.io import wavfile

from convert_audio_wrapper import convert_webm
from speech_recognition_wrapper import speech_to_text_wrapper

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

    def get_new_sample_path(self, username, filetype='wav', no_file_type=False):
        samples = self.get_samples(username)
        username = self.username_to_dirname(username)
        if samples:
            last_sample = max(
                int(name.split('.')[0]) for name in samples
            )
        else:
            last_sample = 0
        if not no_file_type:
            return os.path.join(self.path, username, str(last_sample + 1) + '.' + filetype)
        else:
            return os.path.join(self.path, username, str(last_sample + 1))

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
        return not re.match(r'^\w+$', username)

    @staticmethod
    def is_allowed_file_extension(file: FileStorage) -> bool:
        """
        checks whether mimetype of the file is allowed
        :param file: FileStorage
        :return: True/False
        """
        return True if file.mimetype == "audio/wav" else False

    def save_new_sample(self, username: str, file: FileStorage) -> typing.Tuple[str, str]:
        """
        saves new sample as both .webm and wav with a JSON file
        :param username: str
        :param file: FileStorage
        :return: str wav_path, str recognized_speech
        """
        if not self.user_exists(username):
            self.create_user(username)

        if self.is_allowed_file_extension(file):
            wav_path = self.get_new_sample_path(username, filetype="wav")
            file.save(wav_path)
            print(f"#LOG {self.__class__.__name__}: .wav file saved to: " + wav_path)
        else:
            # not-wav file is temporarily saved
            temp_path = self.get_new_sample_path(username, no_file_type=True)
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

    def get_labels_dict(self):
        usernames = self.get_all_usernames()
        return dict(enumerate(usernames))

    def get_samples_info(self):
        labels = self.get_labels_dict()
        samples = self._load_all_samples()
        return samples, labels

    def _load_all_samples(self):
        labels_dict = self.get_labels_dict()
        labels_inv = {v: k for k, v in labels_dict.items()}
        samples = []
        for username in labels_dict.values():
            user_samples = [
                os.path.join(self.path, username, sample)
                for sample in self.get_samples(username)
            ]
            samples += [
                (user_sample, labels_inv[username])
                for user_sample in user_samples
            ]
        shuffle(samples)
        return samples

    def _simple_wav_read(self, path):
        # TODO(mikra): channels and sample rate
        file = wave.open(path, 'rb')
        data = []
        num_frames = file.getnframes()
        for i in range(num_frames):
            frame = file.readframes(1)
            tmp_data = np.fromstring(frame, dtype='uint8')
            data.extend((tmp_data + 128)/255.)
        return data

    def _fast_wav_read(self, path, chunk_size=64):
        file = wave.open(path, 'rb')
        data = []
        frame = True
        while frame:
            frame = file.readframes(chunk_size)
            tmp_data = np.fromstring(frame, dtype='uint8')
            data.extend((tmp_data + 128)/255.)
        return data

    def _normalize_wav_length(self, data, length):
        # TODO(mikra): resampling!!!
        data = data[0: length]
        if len(data) < length:
            data.extend(np.zeros(length - len(data)))
        return data

    def _normalize_meanmax(self, data):
        return (data - np.mean(data)) / np.max(data)

    def get_data(self, normalized_length=0, verbose=True):
        samples = self._load_all_samples()
        if verbose:
            print('Loading data, found {} samples.'.format(len(samples)))
            print('[|>', end='', flush=True)
        X, y = [], []
        verbose_step = len(samples) // 100
        for sample, label in samples:
            try:
                verbose_step -= 1
                data = self._fast_wav_read(sample)
                if normalized_length:
                    data = self._normalize_wav_length(data, normalized_length)
                X.append(self._normalize_meanmax(np.array(data)))
                y.append(label)
                if verbose and verbose_step == 0:
                    print('\b\b=|>', end="", flush=True)
                    verbose_step = len(samples) // 100
            except Exception as e:
                print(
                    '\n file ' + sample + ' could not be loaded'
                    ' because of an exception: ' + str(e)
                )
        if verbose:
            print(']\n', flush=True)
        return (np.array(X), np.array(y))

    def data_generator(self, batch_size=10, normalized_length=0):
        samples = self._load_all_samples()
        batch, labels = [], []
        for sample, label in samples:
            data = self._fast_wav_read(sample)
            # scipy.io.wavfile is incompatible with 24bit depth
            if normalized_length:
                data = self._normalize_wav_length(data, normalized_length)
            batch.append(data)
            labels.append(label)
            if len(batch) >= batch_size:
                yield np.array(batch), np.array(labels)
                batch, labels = [], []
