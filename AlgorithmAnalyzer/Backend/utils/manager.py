import os
import re
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
        print(self.path)

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

    def add_sample(self, username, sample):
        samples = self.get_samples(username)
        username = self.username_to_dirname(username)
        if samples:
            last_sample = max(
                int(name.split('.')[0]) for name in samples
            )
        else:
            last_sample = 0
        new_path = os.path.join(self.path, username, str(last_sample + 1))
        with open('{}.wav'.format(new_path), 'wb') as new:
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

    def username_to_dirname(self, username):
        '''username: string'''
        '''Convert username, which could include spaces,
         big letters and diacritical marks, to valid directory name'''

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

        if self._invalid_username(temp):
            raise UsernameException(
                'Incorrect username "{}" !'.format(temp)
            )
        return temp
