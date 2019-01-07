from .simple_nn import SimpleNN
from .easy_example import EasyExample

ALG_DICT = {
    'Simple Neural Net': SimpleNN,
    'Random': EasyExample
}

__all__ = ['ALG_DICT']
