import unittest

from utils.textgen import textgen


class TextGeneratorTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.textgen = textgen.TextGenerator("corpus.txt")

    def test_generate_words(self):
        out = self.textgen.generate_words(100)
        self.assertTrue(isinstance(out, list))
        self.assertTrue(isinstance(out[0], str))
        self.assertEqual(len(out), 100)
