import random

from algorithms.base_algorithm import Algorithm


class MultilabelExample(Algorithm):
    """
    As a prediction returns a random user,
    who is identified by a number between 0 and num_classes.
    """
    multilabel = True

    def __init__(self, parameters=None, path=None):
        if path:
            self._load(path)
        elif parameters:
            self.parameters = parameters

    @classmethod
    def get_parameters(cls):
        return {'num_classes': {
            'description': 'The number of clusses to choose from.',
            'type': int,
            'values': list(range(100))
            }
        }

    def train(self, *args, **kwargs):
        pass

    def save(self, path):
        with open(path, 'w') as file:
            file.write(str(self.parameters['num_classes']))

    def _load(self, path):
        with open(path, 'r') as f:
            self.parameters = {
                'num_classes': int(f.read())
            }

    def predict(self, data):
        return random.randint(0, self.parameters['num_classes']), {}
