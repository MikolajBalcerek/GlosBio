from sample_manager.SampleManager import SampleManager


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

    # sample manager
    SAMPLE_MANAGER = SampleManager(SAMPLE_UPLOAD_PATH)


class ProductionConfig(BaseConfig):
    pass


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True


