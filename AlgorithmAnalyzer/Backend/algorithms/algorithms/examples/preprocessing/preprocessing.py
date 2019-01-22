import wave
import numpy as np

import scipy.io.wavfile as wav

from .filters import fir_bandpass


def fast_wav_read(file, chunk_size=64):
    file = wave.open(file, 'rb')
    data = []
    frame = True
    while frame:
        frame = file.readframes(chunk_size)
        tmp_data = np.fromstring(frame, dtype='uint8')
        data.extend((tmp_data + 128)/255.)
    return data


def normalize_wav_length(data, length):
    data = data[0: length]
    if len(data) < length:
        data.extend(np.zeros(length - len(data)))
    return data


def normalize_meanmax(data):
    return (data - np.mean(data)) / np.max(data)


def read_sample(sample, normalized_length=0):
    data = fast_wav_read(sample)
    if normalized_length:
        data = normalize_wav_length(data, normalized_length)
        return normalize_meanmax(np.array(data))
    return data


def join_samples_dicts(sample_dict, labels_dict):
    usernames = sample_dict.keys()
    samples, labels = [], []
    names_dict = {}
    usernum = -1
    for name in usernames:
        usernum += 1
        names_dict[usernum] = name
        for num, label in enumerate(labels_dict[name]):
            if label:
                samples.append(sample_dict[name][num])
                labels.append(usernum)
    return samples, labels, names_dict


def read_samples(samples, labels, normalized_length=0, verbose=False):
    if verbose:
        print('Loading data, found {} samples.'.format(len(samples)))
        print('[|>', end='', flush=True)
    X, y = [], []
    verbose_step = len(samples) // 100
    for sample, label in zip(samples, labels):
        try:
            verbose_step -= 1
            X.append(read_sample(sample, normalized_length))
            y.append(label)
            if verbose and verbose_step == 0:
                print('\b\b=|>', end="", flush=True)
                verbose_step = len(samples) // 100
        except Exception as e:
            print(
                '\n file could not have been loaded'
                ' because of an exception: ' + str(e)
            )
    if verbose:
        print(']\n', flush=True)
    return np.array(X), np.array(y)


def filter_sample_for_human_voice(sample, fs):
    return fir_bandpass(sample, fs, 300, 3000, 50)


def scipy_read_samples(raw_samples):
    samples, rates = [], []
    for sample in raw_samples:
        try:
            fs, smpl = wav.read(sample)
            smpl = filter_sample_for_human_voice(smpl, fs)
            samples.append(smpl)
            rates.append(fs)
        except Exception as e:
            print(
                '\n file could not have been loaded'
                ' because of an exception: ' + str(e)
            )
    return samples, rates
