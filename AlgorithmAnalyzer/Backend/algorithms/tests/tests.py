import hashlib
import unittest
from pathlib import Path

from algorithms.algorithm_manager import (
    algorithm_manager_factory,
    NotTrainedException
)
from algorithms.base_algorithm import AlgorithmException
from algorithms.tests.mocks import TEST_ALG_DICT, AlgorithmMock1
from config import TestingConfig


class TestAlgorithmManager(unittest.TestCase):

    def setUp(self):
        self.am = algorithm_manager_factory(
            TEST_ALG_DICT, TestingConfig.JOB_STATUS_UPDATER_FACTORY,
            '__test__alg__manager'
        )
        self.jsp = TestingConfig.JOB_STATUS_PROVIDER
        self.alg_dict = TEST_ALG_DICT
        self.full_alg_list = list(TEST_ALG_DICT.keys())
        # they differ by mock throwing exceptions
        self.alg_list = ['first_mock', 'second_mock']
        self.raise_alg = 'raise_mock'
        self.params1 = {'some_name': '2'}
        self.params2 = {'param1': '1', 'param2': 'c'}
        self.user_samples = {
            'user1': [0, 1, 2],
            'user2': ['a', 'b', 'c']
        }
        self.user_labels = {
            'user1': [0, 1, 1],
            'user2': [1, 1, 0]
        }
        self.samples = [1, 2, 3, 4]
        self.labels = [0, 1, 2, 0]

    def tearDown(self):
        for alg_name in self.alg_list:
            path = Path('./algorithms/saved_models/' + alg_name)
            for subpath in path.rglob('*'):
                subpath.rmdir()
            if path.exists():
                path.rmdir()

    def test_get_algorithms(self):
        self.assertEqual(self.am.get_algorithms(), self.full_alg_list)

    def test_get_parameters(self):
        for alg in self.alg_list:
            params = self.alg_dict[alg].get_parameters()
            for param in params:
                params[param].pop('type', None)
            self.assertEqual(
                self.am.get_parameters(alg),
                params
            )

    def test_multilabel(self):
        self.assertEqual(self.am('first_mock').multilabel, False)
        self.assertEqual(self.am('second_mock').multilabel, True)

    def test_get_parameter_types(self):
        self.assertEqual(
            self.am.get_parameter_types('first_mock'),
            {'some_name': int}
        )
        self.assertEqual(
            self.am.get_parameter_types('second_mock'),
            {'param1': int, 'param2': str},
        )

    def test_get_description(self):
        for alg in self.alg_list:
            self.assertEqual(
                self.am(alg).get_description(),
                self.alg_dict[alg].__doc__
            )

    def test_update_parameters(self):
        self.assertEqual(
            self.am('second_mock')._update_parameters(self.params2),
            {'param1': 1, 'param2': 'c'}
        )

    def test_train_models(self):
        am = self.am('first_mock')
        jid = self.jsp.create_job_status()
        thread = am._train_models(
            self.user_samples, self.user_labels, self.params1, jid
        )
        thread.join()
        self.assertEqual(am.models.keys(), self.user_labels.keys())
        for usr, mdl in am.models.items():
            self.assertTrue(mdl.called_train)
            self.assertTrue(mdl.called_save)
            self.assertFalse(mdl.called_load)
            md5 = hashlib.md5(usr.encode('utf-8'))
            base_path = f'./algorithms/saved_models/first_mock/'
            base_path += md5.hexdigest()
            self.assertEqual(mdl.save_path, base_path + '/model')
            self.assertTrue(Path(base_path).exists())

    def test_save_models(self):
        mdls = [AlgorithmMock1(), AlgorithmMock1()]
        usrs = ['user1', 'user2']
        am = self.am('first_mock')
        am.models = {
            'user1': mdls[0],
            'user2': mdls[1]
        }
        am._save_models()
        for i in [0, 1]:
            self.assertTrue(mdls[i].called_save)
            self.assertFalse(mdls[i].called_train)
            self.assertFalse(mdls[i].called_load)
            md5 = hashlib.md5(usrs[i].encode('utf-8'))
            base_path = f'./algorithms/saved_models/first_mock/'
            base_path += md5.hexdigest()
            self.assertEqual(mdls[i].save_path, base_path + '/model')
            self.assertTrue(Path(base_path).exists())

    def test_load_model_should_raise_without_model(self):
        with self.assertRaises(NotTrainedException) as ctx:
            self.am('first_mock')._load_model('user1')
        self.assertEqual(
            str(ctx.exception),
            'There is no model of first_mock trained for user1.'
        )

    def test_load_model(self):
        am = self.am('first_mock')
        jid = self.jsp.create_job_status()
        thread = am._train_models(
            self.user_samples, self.user_labels, self.params1, jid
        )
        thread.join()
        # creating new instance to clear everything
        am = self.am('first_mock')
        for u in ['user1', 'user2']:
            self.assertFalse(
                u in am.models
            )
            am._load_model(u)
            self.assertTrue(
                am.models[u].called_load
            )

    def test_train_multilabel_model(self):
        am = self.am('second_mock')
        jid = self.jsp.create_job_status()
        thread = am._train_multilabel_model(
            self.samples, self.labels, self.params2, jid
        )
        thread.join()
        self.assertTrue(hasattr(am, 'model'))
        self.assertTrue(am.model.called_train)
        self.assertTrue(am.model.called_save)
        self.assertFalse(am.model.called_load)
        self.assertTrue(
            Path('./algorithms/saved_models/second_mock').exists()
        )

    def test_load_multilabel_model_should_raise_without_model(self):
        with self.assertRaises(NotTrainedException) as ctx:
            self.am('second_mock')._load_multilabel_model()
        self.assertEqual(
            str(ctx.exception),
            'There is no model of second_mock trained.'
        )

    def test_load_multilabel_model(self):
        am = self.am('second_mock')
        jid = self.jsp.create_job_status()
        thread = am._train_multilabel_model(
            self.samples, self.labels, self.params2, jid
        )
        thread.join()
        # creating new instance to clear everything
        am = self.am('second_mock')
        self.assertFalse(hasattr(am, 'model'))
        am._load_multilabel_model()
        self.assertTrue(hasattr(am, 'model'))
        self.assertIsNotNone(am.model)
        self.assertFalse(am.model.called_train)
        self.assertFalse(am.model.called_save)
        self.assertTrue(am.model.called_load)

    def test_predict_should_raise_without_model(self):
        user, sample = 'user1', 'whatever'
        for alg in self.alg_list:
            with self.assertRaises(NotTrainedException) as ctx:
                self.am(alg).predict(user, sample)
        self.assertEqual(
            str(ctx.exception),
            {
                'second_mock':
                    f'There is no model of {alg} trained.',
                'first_mock':
                    f"There is no model of {alg} trained for {user}."
            }[alg]
        )

    def test_predict_for_multilabel(self):
        am = self.am('second_mock')
        jid = self.jsp.create_job_status()
        thread = am._train_multilabel_model(
            self.samples, self.labels, self.params2, jid
        )
        thread.join()
        user, sample = 'user1', 'whatever'
        res = am.predict(user, sample)
        self.assertEqual(res, (0, {"something": 0}))

    def test_predict_for_binary_label(self):
        am = self.am('first_mock')
        jid = self.jsp.create_job_status()
        thread = am._train_models(
            self.user_samples, self.user_labels, self.params1, jid
        )
        thread.join()
        user, sample = 'user1', 'whatever'
        res = am.predict(user, sample)
        self.assertEqual(res, (False, {"something": "Somethong"}))

    def test_train_for_multilabel_model(self):
        am = self.am('second_mock')
        jid = self.jsp.create_job_status()
        thread = am.train(
            self.samples, self.labels, self.params2, jid
        )
        thread.join()
        self.assertTrue(
            Path('./algorithms/saved_models/second_mock').exists()
        )

    def test_train_for_binary_model(self):
        am = self.am('first_mock')
        jid = self.jsp.create_job_status()
        thread = am.train(
            self.user_samples, self.user_labels, self.params1, jid
        )
        self.assertNotEqual(am.models.keys(), self.user_labels.keys())
        thread.join()
        self.assertEqual(am.models.keys(), self.user_labels.keys())
        for usr, mdl in am.models.items():
            self.assertTrue(mdl.called_train)
            self.assertTrue(mdl.called_save)
            self.assertFalse(mdl.called_load)
            md5 = hashlib.md5(usr.encode('utf-8'))
            base_path = f'./algorithms/saved_models/first_mock/'
            base_path += md5.hexdigest()
            self.assertEqual(mdl.save_path, base_path + '/model')
            self.assertTrue(Path(base_path).exists())

    def test_train_with_raise_mock(self):
        am = self.am(self.raise_alg)
        jid = self.jsp.create_job_status()
        thread = am.train(self.user_samples, self.user_labels, {}, jid)
        thread.join()
        status = self.jsp.read_job_status(jid)
        self.assertIn('error', status)

    def test_load_with_raise_mock(self):
        am = self.am(self.raise_alg)
        base_path = f'./algorithms/saved_models/{self.raise_alg}/'
        Path(base_path).mkdir(parents=True)
        with self.assertRaises(AlgorithmException) as ctx:
            am._load_multilabel_model()
        self.assertEqual(str(ctx.exception), 'load exception')
