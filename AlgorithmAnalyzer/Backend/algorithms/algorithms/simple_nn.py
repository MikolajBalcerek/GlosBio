from tensorflow.python.keras.layers import Activation, Dropout, Dense, Flatten
from tensorflow.python.keras.models import Sequential, load_model
from tensorflow.python.keras.utils.np_utils import to_categorical
from tensorflow.python.keras.backend import clear_session
from tensorflow import reset_default_graph

from algorithms.algorithms.preprocessing import read_samples, read_sample
from algorithms.base_algorithm import Algorithm


class SimpleNN(Algorithm):
    parameters = {
        'epochs': 100,
        'varbosity': 0
    }

    SAMPLE_LENGTH = 4 * 4096

    def __init__(self, parameters=None, path=None):
        self.model = None
        if(parameters):
            self.parameters = parameters
        elif(path):
            self.load(path)

    def _prepare_model(self):
        model = Sequential()

        model.add(Dense(54, input_dim=self.SAMPLE_LENGTH))
        model.add(Dropout(.5))
        model.add(Dense(48))
        model.add(Dropout(.5))
        model.add(Flatten())
        model.add(Dense(2))
        model.add(Activation('sigmoid'))

        model.compile(
            loss='binary_crossentropy',
            optimizer='rmsprop',
            metrics=['accuracy']
        )

        self.model = model

    @classmethod
    def get_parameters(cls):
        return {
            'epochs': {
                'description': 'Number of epochs to train the network.',
                'type': int,
                'values': [10, 50, 100]
            },
            'verbosity': {
                'description': '0 - no console info, 1 - more console info.',
                'type': int,
                'values': [0, 1]
            }
        }

    def train(self, samples, labels):
        print(samples)
        print(labels)  # for some reason gridFS has problems without those prints
        X, y = read_samples(samples, labels, normalized_length=self.SAMPLE_LENGTH)
        y = to_categorical(y)
        self._prepare_model()
        self.model.fit(X, y,
                       epochs=self.parameters['epochs'], validation_split=.25, verbose=self.parameters['verbosity']
                       )

    def predict(self, data):
        data = read_sample(data, normalized_length=self.SAMPLE_LENGTH)
        data = data.reshape((1, self.SAMPLE_LENGTH))
        preds = self.model.predict(data)
        clear_session()
        return bool(preds[0][1] > preds[0][0]), {
            "Probability of being real: ": float(preds[0][1]),
            "Probability of being fake: ": float(preds[0][0])
        }

    def save(self, path):
        print(path)
        self.model.save(path + '.h5')

    def load(self, path):
        reset_default_graph()
        clear_session()
        # those are needed as tensorflow has some problems
        # see: https://github.com/tensorflow/tensorflow/issues/14356
        self.model = load_model(path + '.h5')
