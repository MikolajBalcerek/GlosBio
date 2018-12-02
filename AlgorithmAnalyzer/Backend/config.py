# directory where samples will be stored
SAMPLE_UPLOAD_PATH = './data'

# avaliable classes of samples
ALLOWED_SAMPLE_TYPES = ['train', 'test']

# avaliable filetypes and corresponding allowed extensions
ALLOWED_FILES_TO_GET = {'audio': ['wav', 'webm'],
                        'json': ['json']}

# MongoDB database settings
DATABASE_URL = "127.0.0.1"
DATABASE_PORT = "27018"
DATABASE_NAME = "samplebase"
