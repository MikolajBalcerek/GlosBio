import os
import re
import unicodedata

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from scipy.io import wavfile

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

    def save_new_sample(self, username: str, file: FileStorage) -> str:
        print("LOG: username: {}".format(username))
        if not self.user_exists(username):
            self.create_user(username)
        path = self.get_new_sample_path(username, filetype="webm")
        file.save(path)
        return path

    def username_to_dirname(self, username: str):
        '''
        Convert username, which could include spaces,
        big letters and diacritical marks, to valid directory name
        '''
        temp = unicodedata.normalize('NFD', username.lower()).encode('ascii', 'ignore').decode('utf-8')
        temp = temp.replace(" ", "_")
        
        if self._invalid_username(temp):
            raise UsernameException(
                'Incorrect username "{}" !'.format(temp)
            )
        return secure_filename(temp)
