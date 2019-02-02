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


def normalize_signal_length(signal, length):
    if len(signal) >= length:
        return signal[0: length - 1]
    else:
        zeros = np.zeros(length - len(signal))
        return np.append(signal, zeros)


def normalize_meanmax(data):
    return (data - np.mean(data)) / np.max(data)


def read_sample(sample, normalized_length=0):
    data = fast_wav_read(sample)
    if normalized_length:
        data = normalize_signal_length(data, normalized_length)
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


def filter_sample_for_human_frequency(sample, sampling_rate):
    smpl_type = sample.dtype
    return fir_bandpass(sample, sampling_rate, 100, 8000, 50).astype(smpl_type)


def rms(array):
    arr = array.astype(np.float32)
    # dtype is set to float so as to omit possible buffer overflows
    return np.sqrt(np.dot(arr, arr) / len(array))


def remove_beginning_silence(sample, rate, loudness_fraction=1./8):
    win_len = int(.01 * rate)  # 10 ms
    maximal = np.log2(np.max(sample))
    # max to go around bit depth
    eps = 2 ** int(maximal * loudness_fraction)  # 1 / 8th max loudness
    i = 0
    while i + win_len < len(sample) and rms(sample[i:i + win_len]) < eps:
        i += win_len
    return sample[i:]


def read_and_preprocess_samples(
    sample_files,
    filter_for_human_voice_frequency=True,
    remove_silence_at_beginning=True,
    normalize_length=None
):
    samples, rates = [], []
    for sample in sample_files:
        try:
            fs, smpl = wav.read(sample)
            if len(smpl.shape) > 1:
                sample = sample[0]  # if there are more channels
            if filter_for_human_voice_frequency:
                smpl = filter_sample_for_human_frequency(smpl, fs)
            if remove_silence_at_beginning:
                smpl = remove_beginning_silence(smpl, fs)
            if normalize_length and type(normalize_length) == type(int):
                smpl = normalize_signal_length(smpl, normalize_length)
            samples.append(smpl)
            rates.append(fs)
        except Exception as e:
            print(
                '\n file could not have been loaded'
                ' because of an exception: ' + str(e)
            )
    return samples, rates
