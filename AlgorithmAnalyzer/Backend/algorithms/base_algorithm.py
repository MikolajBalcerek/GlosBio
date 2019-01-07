from abc import ABCMeta, abstractmethod

from algorithms.abstract_class_method import abstractclassmethod


class Algorithm:
    """
    This is an interface for all algorithms to be added.
    In order to add an algorithm to the app, one must:
        - derive the algorithm class after this class
        - add it to ALG_DICT in algorithms/algorithms/__init__.py
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, parameters=None, path=None):
        """
        Each algorithm should have a constructor of this form,
        if the parameter `path` is given, the model should be loaded.
        If the parameter `parameters` is given, the model parameters
        will be set up to train the model with those parameters.
        The `parameters` argument is of the form:
        {
            'parameter_name':  value
        }
        and it's keys are the same as the keys from get_parameters().keys().
        """
        if(path):
            self.load(path)
        if(parameters):
            self.parameters = parameters

    @abstractclassmethod
    def get_parameters(cls):
        """
        This method should return a dicionary of parameters of the form
        {
            'parameter_name': {
                'description': 'a description of the parameter',
                'type': int / str / float
                'values': [
                    a list of values the parameter can take, first being the default
                ]
            }
        }
        Those parameters can be selected by the user before training the model.
        If no parameters are needed just return an empty dictionary.
        """
        pass

    @abstractmethod
    def save(self, path):
        """
        This method should save the model at a given path.
        """
        pass

    @abstractmethod
    def load(self, path):
        """
        This method should load the model from given path.
        """
        pass

    @abstractmethod
    def train(self, samples, labels):
        """
        This method should train the model on samples and labels from the database,
        samples are of file-object type and labels are either 0 or 1:
        0 - the recording doesn't belong to the speaker
        1 - the recording does belong to the speaker
        """
        pass

    @abstractmethod
    def predict(self, sample):
        """
        This method should predict if sample is real or fake and return a pair:
            True / False, {'message0': value0, 'message1': value1, ...}
        where the messages and values are ment to describe the probability of classification,
        and will be displayed to the end user.
        If such probabilities cannot be given, just return an empty dictionary instead.
        """
        pass
