import numpy as np
from python_speech_features import mfcc


def get_mfcc(sample, rate):
    return mfcc(sample, rate, winfunc=np.hamming)
