from .examples.simple_nn import SimpleNN
from .examples.easy_example import EasyExample
from .examples.multilabel_example import MultilabelExample
from .examples.dtw import DTWExample

ALG_DICT = {
    'Simple Neural Net': SimpleNN,
    'Random': EasyExample,
    'Multilabel Random': MultilabelExample,
    'Dynamic Time Warping': DTWExample
}

__all__ = ['ALG_DICT']
