import os
import markovify


class TextGenerator:
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "corpus1.txt")
        with open(path) as f:
            text = f.read()
        self.chain = markovify.Text(text).chain

    def generate_words(self, n: int) -> str:
        '''
        generate string with n words
        :params n: int - no. words to generate
        '''
        out = []
        count = 0
        while len(out) < n:
            out += self._non_empty_sentence()
            count += 1
            if count > 100:
                raise ValueError("Could not generate enough words")
        return out[:n]

    def _non_empty_sentence(self) -> str:
        out = None
        count = 0
        while not out:
            out = self.chain.walk()
            count += 1
            if count > 100:
                raise ValueError("Could not generate non-empty sentence")
        return out
