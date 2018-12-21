# not app related configs
ALLOWED_PLOT_TYPES_FROM_SAMPLES = ['mfcc']


class BaseConfig(object):
    DEBUG = False
    TESTING = False

    # directory where samples will be stored
    SAMPLE_UPLOAD_PATH = './data'

    # available classes of samples
    ALLOWED_SAMPLE_TYPES = ['train', 'test']

    # available filetypes and corresponding allowed extensions
    ALLOWED_FILES_TO_GET = {'audio': ['wav', 'webm'],
                            'json': ['json']}

    # allowed plots' file extensions
    ALLOWED_PLOT_FILE_EXTENSIONS = ['pdf', 'png']

    # allowed plot from samples' types
    object.ALLOWED_PLOT_TYPES_FROM_SAMPLES = ALLOWED_PLOT_TYPES_FROM_SAMPLES


class ProductionConfig(BaseConfig):
    pass


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True


