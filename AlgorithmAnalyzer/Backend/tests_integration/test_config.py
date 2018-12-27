import unittest

from config import *
from main import app


class TestConfigVariableSetting(unittest.TestCase):
    def test_testing_app_variables(self):
        """ tests if app takes correct variables after being set up as test"""
        self.app = app
        self.app.config.from_object('config.TestingConfig')

        self.assertTrue(self.app.config['TESTING'],
                        "TESTING app variable"
                        "should be set to True")

        self.assertFalse(self.app.config['DEBUG'], "DEBUG app variable"
                                                  "should be set to False")

    def test_production_app_variables(self):
        """ tests if app takes correct variables after being set up as production"""
        self.app = app
        self.app.config.from_object('config.ProductionConfig')

        self.assertFalse(self.app.config['TESTING'],
                         "TESTING app variable"
                         "should be set to False")

        self.assertFalse(self.app.config['DEBUG'], "DEBUG app variable"
                                                   "should be set to False")

    def test_development_app_variables(self):
        """ tests if app takes correct variables after being set up as development"""
        self.app = app
        self.app.config.from_object('config.DevelopmentConfig')

        self.assertFalse(self.app.config['TESTING'],
                         "TESTING app variable"
                         "should be set to False")

        self.assertTrue(self.app.config['DEBUG'], "DEBUG app variable"
                                                  "should be set to True")


if __name__ == '__main__':
    unittest.main()
