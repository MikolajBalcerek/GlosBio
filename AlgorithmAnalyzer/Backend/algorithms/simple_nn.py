
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Activation, Dropout, Dense

from utils import SampleManager
from algorithms.algorithm import Algorithm


class SimpleNN(Algorithm):
    def __init__(self):
        self.model = None

    def prepare_model(self, num_classes):
        model = Sequential()

        model.add(Dense(54, input_dim=4096))
        model.add(Dropout(.5))
        model.add(Dense(48))
        model.add(Dropout(.5))
        model.add(Dense(num_classes))
        model.add(Activation('softmax'))

        model.compile(
            loss='sparse_categorical_crossentropy',
            optimizer='rmsprop',
            metrics=['accuracy']
        )

        self.model = model

    def train(self, data=None):
        sm = SampleManager('data')
        samples, labels_dict = sm.get_samples_info()
        if data:
            X, y = data
        else:
            X, y = sm.get_data(normalized_length=4096)
        self.prepare_model(len(labels_dict))
        self.model.fit(X, y, epochs=100, validation_split=.25, verbose=2)

    def get_model(self):
        return self.model
