from sample_manager.SampleManager import SampleManager


class BaseConfig(object):

    # Debug from Flask's documentation:
    # 'If you enable debug support the server will reload itself on code changes,
    #  and it will also provide you with a helpful debugger if things go wrong.'
    #  (on localhost:port)
    DEBUG = False

    # Testing from Flask's documentation:
    # 'What this does is disable error catching during request handling,
    # so that you get better error reports when performing test requests
    # against the application.'
    # also allows to setup a test client to send requests using
    # werkezeug (Flask's) tools
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


