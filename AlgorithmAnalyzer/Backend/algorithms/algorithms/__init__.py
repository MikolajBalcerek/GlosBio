from .simple_nn import SimpleNN
from .easy_example import EasyExample
from .multilabel_example import MultilabelExample

ALG_DICT = {
    'Simple Neural Net': SimpleNN,
    'Random': EasyExample,
    'Multilabel Random': MultilabelExample
}

__all__ = ['ALG_DICT']
