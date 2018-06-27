
import numpy as np
from sklearn import preprocessing
import python_speech_features as psf


def calculate_mfcc_point(sample_rate, signal):
    """
    calculates mfcc features of single data point
    """
    # TODO: find better parameters
    return psf.mfcc(signal, samplerate=sample_rate, winlen=0.025, winstep=0.01, numcep=13,
             nfilt=26, nfft=512, lowfreq=0, highfreq=None, preemph=0.97,
             ceplifter=22, appendEnergy=True)


def calculate_mfcc_list(sound_list):
    """
    uses the above function to calculate mfcc of list of data points
    """
    mfccs = []
    # TODO: maybe add other things like logfbang or deltas
    for (rate, signal) in sound_list:
        mfcc = calculate_mfcc_point(rate, signal)
        mfcc = preprocessing.scale(mfcc)
        mfccs.append(mfcc)
    return mfccs


def calculate_mfcc_dict(data, verbose=False):
    """
    calculates mfcc features of the whole data kept in a dict
    that is returned from get_data in DataPreparation.load_data
    :param data the dictionary containing data:
    :param verbose True iff console output should be given:
    :return dict with features being mfcc vectors:
    """
    for id in data:
        if verbose:
            print("calculating mfcc of {}".format(id))
        data[id] = calculate_mfcc_list(data[id])
    return data


def mfcc_dict_to_matrix(data):
    """
    transforms data contained in dict to np.array
    :param data a dictionary containing mfcc features:
    :return np.array of shape (num_data_points, num_features) and vector of labels:
    """
    X, y = [], []
    for id in data:
        for feat in data[id]:
            X.append(np.array(feat[1]))
            y.append(id)
    return np.stack(X, axis=1).T, np.array(y)


def calculate_mfcc(data, verbose=False):
    """
    the main function of the module, that calculates matrices of mfcc features
    applies directly to result of get_data from DataPreparation.load_data

    """
    data = calculate_mfcc_dict(data, verbose)
    return mfcc_dict_to_matrix(data)


if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from DataPreparation.load_data import get_data
    train, test = get_data()
    X, y = calculate_mfcc(train)
    print(X.shape)
    print(y.shape)

