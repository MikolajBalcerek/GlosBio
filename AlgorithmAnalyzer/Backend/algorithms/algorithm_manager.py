
from Backend.utils import SampleManager
from simple_nn import SimpleNN


class AlgorithManager:
    ALG_DICT = {
        'simple_nn': SimpleNN
    }

    def __init__(self, alg_name, *args, **kwargs):
        self.algorithm = self.ALG_DICT[alg_name](*args, **kwargs)

    def train(self, *args, **kwargs):
        self.algorithm.train(*args, **kwargs)

    def predict(self, sample):
        self.algorithm.predict(sample)
