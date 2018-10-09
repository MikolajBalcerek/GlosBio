import os
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

class SampleManager:
    def __init__(self, path):
        '''path:  string or path; path to root directory'''
        
        self.path = os.path.normpath(path) 
        print(self.path)
        
    def get_all_usernames(self):
        d = []
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            d.extend(dirnames)
            break
        return d

    def user_exists(self, username):
        user = self.username_to_dirname(username)
        return os.path.isdir(os.path.join(self.path, user))

    def create_user(self, username):
        user = self.username_to_dirname(username)
        if not self.user_exists(username):
            os.makedirs(os.path.join(self.path, user))
        else:
            '''error handling?'''
            pass
    
    def get_samples(self, username):
        user = self.username_to_dirname(username)
        pass

    def add_sample(self, username, sample):
        pass
    def username_to_dirname(self, username):
        '''username: string'''
        '''Convert username, which could include spaces, big letters and diacritical marks, to valid directory name'''
        
        temp = username.lower()
        d = {"ą": "a",
                "ć": "c",
                "ę": "e",
                "ł":"l",
                "ó":"o",
                "ś": "s",
                "ź":"z",
                "ż": "z"}
        for diac, normal in d.items():
            temp = temp.replace(diac, normal)
        temp = temp.replace(" ", "_")
        return temp
        
        
        
