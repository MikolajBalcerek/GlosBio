from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers.core import Flatten, Dense, Dropout
from tensorflow.python.keras.layers.convolutional import Convolution2D, MaxPooling2D, ZeroPadding2D
from tensorflow.python.keras.optimizers import SGD
from tensorflow import reset_default_graph, get_default_graph

from algorithms.base_algorithm import Algorithm, AlgorithmException
from .preprocessing.preprocessing import read_and_preprocess_samples
from .preprocessing.feature_extraction import get_mfccs


class VGG_16(Algorithm):
    """
    Cokolwiek.
    """
    multilabel = True
    graph = get_default_graph()

    def __init__(self, parameters=None, path=None):
        pass

    @classmethod
    def get_parameters(cls):
        return {}

    def train(self, samples, labels):
        samples, rates = read_and_preprocess_samples(samples)
        mfccs = [get_mfccs(sample, rate) for sample, rate in zip(samples, rates)]
        # y = self.to_categorical(y)
        # with SimpleNN.tensorflow_graph.as_default():
        #     try:
        #         self._prepare_model()
        #         self.model.fit(X, y,
        #                        epochs=self.parameters['epochs'], validation_split=.25, verbose=self.parameters['verbosity']
        #                        )
        #     except Exception as e:
        #         raise AlgorithmException(str(e))


    def save(self, *args, **kwargs):
        pass

    def predict(self, data):
        return bool(0), {}

    def _prepare_model(self):
        model = Sequential()
        model.add(ZeroPadding2D((1, 1), input_shape=(3, 224, 224)))
        model.add(Convolution2D(64, 3, 3, activation='relu'))
        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(64, 3, 3, activation='relu'))
        model.add(MaxPooling2D((2, 2), strides=(2, 2)))

        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(128, 3, 3, activation='relu'))
        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(128, 3, 3, activation='relu'))
        model.add(MaxPooling2D((2, 2), strides=(2, 2)))

        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(256, 3, 3, activation='relu'))
        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(256, 3, 3, activation='relu'))
        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(256, 3, 3, activation='relu'))
        model.add(MaxPooling2D((2, 2), strides=(2, 2)))

        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(512, 3, 3, activation='relu'))
        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(512, 3, 3, activation='relu'))
        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(512, 3, 3, activation='relu'))
        model.add(MaxPooling2D((2, 2), strides=(2, 2)))

        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(512, 3, 3, activation='relu'))
        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(512, 3, 3, activation='relu'))
        model.add(ZeroPadding2D((1, 1)))
        model.add(Convolution2D(512, 3, 3, activation='relu'))
        model.add(MaxPooling2D((2, 2), strides=(2, 2)))

        model.add(Flatten())
        model.add(Dense(4096, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(4096, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(1000, activation='softmax'))
        return model


if __name__ == "__main__":
    im = cv2.resize(cv2.imread('cat.jpg'), (224, 224)).astype(np.float32)
    im[:,:,0] -= 103.939
    im[:,:,1] -= 116.779
    im[:,:,2] -= 123.68
    im = im.transpose((2, 0, 1))
    im = np.expand_dims(im, axis=0)

    # Test pretrained model
    model = VGG_16('vgg16_weights.h5')
    sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(optimizer=sgd, loss='categorical_crossentropy')
    out = model.predict(im)
