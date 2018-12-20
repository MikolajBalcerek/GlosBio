from pydub import AudioSegment
from io import BytesIO


def convert_webm_to_format(source_bytesIO: BytesIO, format : str = "wav"):
    """ Helper function converting webm to wav so it can be handled
   by mainstream libraries

   :param source_bytesIO: BytesIO object of source file
   :param format: intended format without ., e.g. wav
   """
    export_file_bytesIO_in_memory = BytesIO()

    sound = AudioSegment.from_file(
        source_bytesIO,
        codec="opus"
    ).export(export_file_bytesIO_in_memory, format=format)

    return export_file_bytesIO_in_memory

