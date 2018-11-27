import os
from random import shuffle
import wave

import numpy as np

from .SampleManager import SampleManager


class DataManager(SampleManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
