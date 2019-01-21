from abc import ABCMeta, abstractmethod, abstractclassmethod


class AlgorithmException(Exception):
    """
    This exception is meant to be thrown at any point
    in the algorithm. If something goes wrong,
    the error with the message given.
    """
    def __init__(self, message):
        super().__init__(self, message)
        self.message = message

    def __str__(self):
        return self.message


class Algorithm(metaclass=ABCMeta):
    """
    This is an interface for all algorithms to be added.
    In order to add an algorithm to the app, one must:
        - derive the algorithm class from this class
        - add it to ALG_DICT in algorithms/algorithms/__init__.py

    Attributes:
        multilabel - by default it's False. If so, a sperate model will be used and trained for
        each user. The labels wil be 0/1 depending on samples being marked as fake or not.
        If multilabel=True, there will be only one multilabeled model trained on all samples, and the
        labels will be between 0 and the number of current users.

    Docstring:
        the docstring of an algorithm that derives from this class will be displayed
        to the user as a description of the algorithm.
    """

    multilabel = False

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
        An example implementation:

        def __init__(self, parameters=None, path=None):
            if(path):
                # load the model from a given path
            if(parameters):
                self.parameters = parameters
        """

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

    @abstractmethod
    def save(self, path):
        """
        This method should save the model at a given path.
        """

    @abstractmethod
    def train(self, samples, labels):
        """
        This method should train the model on samples and labels from the database,
        samples are of file-object type and depending on `multilabel` attibute:
            multilabel=False:
                labels are either 0 or 1:
                0 - the recording doesn't belong to the speaker
                1 - the recording does belong to the speaker
            multilabel=True:
                labels are between 0 and the number of current users
        """

    @abstractmethod
    def predict(self, sample):
        """
        This method should predict the label of sample.
        If multilabel=False
            It should predict if sample is real or fake and return a pair:
                True / False, {'message0': value0, 'message1': value1, ...}
            or 0 / 1, {'message0': value0, 'message1': value1, ...}.
        If multilabel=True
            It should return a pair
                label, {'message0': value0, 'message1': value1, ...}
            where the label is the number of user, the same as given in training.
        Messages and values are ment to describe the probability of classification,
        but can by anything else and will be displayed to the end user.
        If such probabilities cannot be given, just return an empty dictionary instead.
        """

    def set_status_updater(self, updater):
        """
        If model is multilabel, this method will be called before training.
        It will pass `updater` - an object, that can be used to
        pass the status of training to the user.
        Always training is done in the background and each training 'session' has
        it's own id, by wich user can check the status at any tme.

        Example implementation:

            def set_status_updater(self, updater):
                self.status_updater = updater

        Then use inside of train:

            def train(self, samples, labels):
                # prepare model
                for num, batch in enumerate(data_batches):
                    # train(bach) code here
                    batches_done = num / len(data_batches)
                    self.status_updater.update(progress=batches_done)

        Object `updater` has only one method:
            updater.update(progress: float, finished: bool = False, error: str = None)

        For not multilabel models updates are done authomatically based on number of users.
        """
        pass
