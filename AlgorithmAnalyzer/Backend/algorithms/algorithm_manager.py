from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import hashlib
from pathlib import Path
from typing import List, Tuple, Dict

from algorithms.algorithms import ALG_DICT


def background_task(pool_executor):
    """
    Creates a decorator, that makes a function
    executed in the background using pool_executor
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
    This class servs as an api between the application and algorithms,
    """
    # TODO(mikra): add multiclass clasyfication,
    # TODO(all): shall this be changed to functions?
    thread_pool_executor = ThreadPoolExecutor()

    def __init__(self, algorithm_name):
        self.models = {}
        self.algorithm_name = algorithm_name
        self.algorithm = ALG_DICT[algorithm_name]

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

    @background_task(thread_pool_executor)
    def train_models(self, samples: dict, labels: dict, parameters: dict = None):
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
        self.save_models()

    def save_models(self):
        """
        Saves all models to saved_models/algorithm_name/user_name,
        using model's save function.
        """
        for name in self.models:
            model = self.models[name]
            Path(F'./algorithms/saved_models/{self.algorithm_name}').mkdir(parents=True, exist_ok=True)
            md5 = hashlib.md5(name.encode('utf-8'))
            model.save(f'./algorithms/saved_models/{self.algorithm_name}/{md5.hexdigest()}')

    def predict(self, user: str, file) -> Tuple[bool, Dict[str, float]]:
        """
            Returns model's predictions if a sample `file`
            contains `user`'s voice. Returns
            True/False if yes/no and an addictional dictionary,
            with information about predictiona (probabilities).
            :param user: name of the user who is predicted
            :param file: wav-file-like object, containing the sample
        """
        self.load_model(user)
        return self.models[user].predict(file)

    def load_model(self, user: str):
        """
        Load user's model from saved_models/algorithm_name/user_name,
        using model's load function.
        :param user: the name of the user for wich the model should be loaded
        """
        # TODO(mikra): take care of models load returning errors!!!
        md5 = hashlib.md5(user.encode('utf-8'))
        base_path = f'./algorithms/saved_models/{self.algorithm_name}/{md5.hexdigest()}'
        self.models[user] = self.algorithm(path=base_path)

    def validate_models(self):
        pass
