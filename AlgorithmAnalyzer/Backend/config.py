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
ALLOWED_PLOT_TYPES_FROM_SAMPLES = ['mfcc']

# MongoDB database settings
DATABASE_URL = "127.0.0.1"
DATABASE_PORT = "27018"
DATABASE_NAME = "samplebase"
