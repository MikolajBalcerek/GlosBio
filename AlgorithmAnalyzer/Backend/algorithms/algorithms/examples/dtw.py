from algorithms.base_algorithm import Algorithm

from .preprocessing.preprocessing import scipy_read_samples
from .preprocessing.feature_extraction import get_mfcc

class DTWExample(Algorithm):
    """
    Weryfikacja za pomocą DTW, z cechami MFCC.
    """

    def __init__(self, parameters=None, path=None):
        pass

    @classmethod
    def get_parameters(cls):
        return {}

    def train(self, raw_samples, labels):
        samples = []
        if raw_samples:
            raw_samples, freqs = scipy_read_samples(raw_samples)
            for i, sample in enumerate(raw_samples):
                samples.append(get_mfcc(sample, freqs[i]))
            print(samples[0].shape)

    def save(self, path):
        pass

    def predict(self, data):
        return 0, {}
