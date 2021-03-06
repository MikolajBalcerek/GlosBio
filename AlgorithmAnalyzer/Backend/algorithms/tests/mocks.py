from algorithms.base_algorithm import Algorithm, AlgorithmException


class BaseAlgorithmMock(Algorithm):
    def __init__(self, path=None, parameters=None):
        self.called_save = False
        self.called_train = False
        self.called_load = False
        self.save_path = None

        if parameters:
            self.parameters = parameters
        if path:
            self.called_load = True

    def save(self, path):
        self.called_save = True
        self.save_path = path

    def train(self, samples, labels):
        self.called_train = True


class AlgorithmMock1(BaseAlgorithmMock):
    """A docstring."""

    @classmethod
    def get_parameters(cls):
        return {
            'some_name': {
                'description': "Something.",
                'type': int,
                'values': [1, 2, 3]
            }
        }

    def predict(self, data):
        return False, {"something": "Somethong"}


class AlgorithmMock2(BaseAlgorithmMock):
    """Docstring 2."""

    multilabel = True

    @classmethod
    def get_parameters(cls):
        return {
            'param1': {
                'description': "Param 1.",
                'type': int,
                'values': [1, 2, 3]
            },
            'param2': {
                'description': "Param 2.",
                'type': str,
                'values': ['a', 'b', 'c']
            }
        }

    def train(self, samples, labels):
        super().train(samples, labels)
        self.num_classes = max(labels)

    def predict(self, data):
        return 0, {"something": 0}


class RaisingAlgorithmExceptionMock(BaseAlgorithmMock):

    multilabel = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'path' in kwargs:
            raise AlgorithmException('load exception')

    @classmethod
    def get_parameters(cls):
        return {}

    def train(self, samples, labels):
        super().train(samples, labels)
        raise AlgorithmException("train exception")

    def predict(self, sample):
        super().predict(sample)
        raise AlgorithmException('predict exception')

    def save(self, path):
        super().save(path)
        raise AlgorithmException('path exception')


TEST_ALG_DICT = {
    'first_mock': AlgorithmMock1,
    'second_mock': AlgorithmMock2,
    'raise_mock': RaisingAlgorithmExceptionMock
}
