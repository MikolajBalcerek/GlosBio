import os
import re
import unicodedata

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from scipy.io import wavfile
from pathlib import Path

''''''''''''''''
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

    def sample_exists(self, username, type, sample):
        return Path(os.join(self.get_user_dirpath(username, type), sample)).exists()

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

    def get_new_sample_path(self, username, set_type="train", filetype="wav"):
        samples = self.get_samples(username, set_type)
        username = self.username_to_dirname(username)
        if samples:
            last_sample = max(
                int(name.split('.')[0]) for name in samples
            )
        else:
            last_sample = 0
        if set_type == 'test':
            return os.path.join(self.path, username, set_type, str(last_sample + 1) + '.' + filetype)
        else:
            return os.path.join(self.path, username, str(last_sample + 1) + '.' + filetype)

    def get_user_dirpath(self, username, type='train'):
        if type == 'train':
            return os.path.join(self.path, self.username_to_dirname(username))
        else:
            return os.path.join(self.path, type,  self.username_to_dirname(username))

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

    def save_new_sample(self, username: str, file: FileStorage, type: str) -> str:
        if not self.user_exists(username):
            self.create_user(username)
        path = self.get_new_sample_path(username, set_type=type, filetype="webm")
        file.save(path)
        return path

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
