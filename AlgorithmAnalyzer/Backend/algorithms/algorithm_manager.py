from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import hashlib
from pathlib import Path
from typing import List, Tuple, Dict

from algorithms.algorithms import ALG_DICT


def background_task(pool_executor):
    """
    Creates a decorator, that makes a function
    executed in the background using pool_executor.
    :param pool_executor:
        An executor for running task in the background.
    """
    def decorator(task):
        @wraps(task)
        def in_background(*args, **kwargs):
            fut = pool_executor.submit(task, *args, **kwargs)
            return fut
        return in_background
    return decorator


class AlgorithmManager:
    """
    This class servs as an api between the application and algorithms.
    """
    # TODO(all): shall this be changed to functions?
    thread_pool_executor = ThreadPoolExecutor()

    def __init__(self, algorithm_name):
        self.models = {}
        self.algorithm_name = algorithm_name
        self.algorithm = ALG_DICT[algorithm_name]

    @property
    def multilabel(self):
        return self.algorithm.multilabel

    @classmethod
    def get_algorithms(cls) -> List[str]:
        """
        Returns a list of all available algorithms.
        """
        return list(ALG_DICT.keys())

    @classmethod
    def get_parameters(cls, algorithm: str) -> Dict[str, dict]:
        """
        Returns the list of possible parameters of an algorithm,
        int the form
            {
                'param_name': {
                    'description': "blah-blah-blah",
                    'values': [list of possible values]
                }
            }
        :param algorithm: name of the algorithm
        """
        raw_parameters = ALG_DICT[algorithm].get_parameters()
        for param in raw_parameters:
            raw_parameters[param].pop('type', None)
        return raw_parameters

    @classmethod
    def get_parameter_types(cls, algorithm: str) -> dict:
        """
        Returns the dictionary of types of parameters:
            {
                'param_name': int/str/float
            }
        :param algorithm: name of the algorithm
        """
        params = ALG_DICT[algorithm].get_parameters()
        return {key: params[key]['type'] for key in params}

    def _update_parameters(self, parameters: dict):
        param_dict = self.algorithm.get_parameters()
        for name in param_dict:
            parameters[name] = param_dict[name]['type'](parameters[name])
        return parameters

    def _train_models(self, samples: dict, labels: dict, parameters: dict = None):
        """
        Trains a model for each user for a given algorithm,
        and then saves the model to `saved_models` directory
        """
        # TODO(mikra): add SocketIO and/or Redis communication
        usernames = list(labels.keys())
        parameters = self._update_parameters(parameters)
        for username in usernames:
            model = self.algorithm(parameters=parameters)
            model.train(samples[username], labels[username])
            self.models[username] = model
        self._save_models()

    def _save_models(self):
        """
        Saves all models to saved_models/algorithm_name/user_name,
        using model's save function.
        """
        for name in self.models:
            model = self.models[name]
            Path(f'./algorithms/saved_models/{self.algorithm_name}').mkdir(parents=True, exist_ok=True)
            md5 = hashlib.md5(name.encode('utf-8'))
            model.save(f'./algorithms/saved_models/{self.algorithm_name}/{md5.hexdigest()}')

    def _load_model(self, user: str):
        """
        Load user's model from saved_models/algorithm_name/user_name,
        using model's load function.
        :param user: the name of the user for wich the model should be loaded
        """
        # TODO(mikra): take care of models load returning errors!!!
        md5 = hashlib.md5(user.encode('utf-8'))
        base_path = f'./algorithms/saved_models/{self.algorithm_name}/{md5.hexdigest()}'
        self.models[user] = self.algorithm(path=base_path)

    def _train_multilabel_model(self, samples: list, labels: list, parameters: dict):
        parameters = self._update_parameters(parameters)
        self.model = self.algorithm(parameters=parameters)
        self.model.train(samples, labels)
        self._save_multilabel_model()

    def _save_multilabel_model(self):
        Path(f'./algorithms/saved_models/{self.algorithm_name}').mkdir(parents=True, exist_ok=True)
        self.model.save(f'./algorithms/saved_models/{self.algorithm_name}/{self.algorithm_name}')

    def _load_multilabel_model(self):
        path = f'./algorithms/saved_models/{self.algorithm_name}/{self.algorithm_name}'
        self.model = self.algorithm(path=path)

    def predict(self, user: str, file) -> Tuple[bool, Dict[str, float]]:
        """
            Returns model's predictions if a sample `file`
            contains `user`'s voice. Returns
            True/False if yes/no and an addictional dictionary,
            with information about predictiona (probabilities).
            :param user: name of the user who is predicted
            :param file: wav-file-like object, containing the sample
        """
        if self.algorithm.multilabel:
            self._load_multilabel_model()
            return self.model.predict(file)
        else:
            self._load_model(user)
            return self.models[user].predict(file)

    def train(self, samples, labels, parameters):
        if self.algorithm.multilabel:
            self._train_multilabel_model(samples, labels, parameters)
        else:
            self._train_models(samples, labels, parameters)

    def validate_models(self):
        pass
