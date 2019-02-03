import numpy as np

from algorithms.base_algorithm import Algorithm
from .preprocessing.preprocessing import read_and_preprocess_samples
from .preprocessing.feature_extraction import get_mfccs


class DTWExample(Algorithm):
    """
    Weryfikacja za pomocą DTW, z cechami MFCC.
    """

    def __init__(self, parameters=None, path=None):
        self.num_vectors = 13
        self.bad_mfcc = []
        self.mfccs = []
        if path:
            self.bad_mfcc = np.load(path + 'arr.npy')
            with open(path + 'ths', 'r') as f:
                self.threshold = float(f.read())

    @classmethod
    def get_parameters(cls):
        return {}

    def train(self, raw_samples, labels):
        raw_samples = [s for s, l in zip(raw_samples, labels) if l]
        if not raw_samples:
            return
        raw_samples, freqs = read_and_preprocess_samples(raw_samples)
        for sample, fs in zip(raw_samples, freqs):
            mfccs = get_mfccs(sample, fs, padding_length=2, num_vectors=self.num_vectors)
            self.mfccs.append(mfccs)
        self.bad_mfcc = self.mfccs[-1]
        # TODO: add option for mutual comparison
        if len(self.mfccs) > 1:
            self.threshold = np.max([self.dtw(mfcc, self.bad_mfcc) for mfcc in self.mfccs[:-1]])
        else:
            self.threshold = 0

    def dtw(self, arr1, arr2):
        # TODO: add windowing
        dtw_mat = np.zeros((self.num_vectors + 1, self.num_vectors + 1), dtype=arr1.dtype)
        dtw_mat[:, 0] = np.Infinity
        dtw_mat[0, :] = np.Infinity
        dtw_mat[0, 0] = 0
        for i in range(1, self.num_vectors + 1):
            for j in range(1, self.num_vectors + 1):
                cost = self.dist(arr1[i - 1, :], arr2[j - 1, :])
                mini = min(dtw_mat[i - 1, j], dtw_mat[i, j - 1], dtw_mat[i - 1, j - 1])
                dtw_mat[i, j] = cost + mini
        # print(dtw_mat)
        return dtw_mat[self.num_vectors, self.num_vectors]

    def dist(self, arr1, arr2):
        a1 = arr1.astype(dtype=np.float32)
        a2 = arr2.astype(dtype=np.float32)
        return np.sqrt(np.dot(a1 - a2, a1 - a2))

    def save(self, path):
        # TODO: make this nicer, add indicator
        if len(self.bad_mfcc):
            np.save(path + "arr", self.bad_mfcc)
            with open(path + "ths", 'w') as f:
                f.write(str(self.threshold))

    def predict(self, data):
        if len(self.bad_mfcc):
            smpls, fss = read_and_preprocess_samples([data])
            mfcc = get_mfccs(smpls[0], fss[0], padding_length=2, num_vectors=self.num_vectors)
            dtw_dist = self.dtw(mfcc, self.bad_mfcc)
            return bool(dtw_dist < self.threshold), {
                "Threshold": self.threshold, "Calculated dtw_dist": dtw_dist
            }
        else:
            return 0, {}
