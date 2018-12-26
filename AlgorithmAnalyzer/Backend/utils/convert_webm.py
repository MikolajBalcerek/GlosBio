from pydub import AudioSegment
from io import BytesIO


def convert_webm_to_format_from_bytesIO(source_bytesIO: BytesIO, format : str = "wav"):
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

def convert_webm_to_format_from_path(source_path: str, destination_path: str,
                           format : str = "wav"):
    """ Helper function converting webm to wav so it can be handled
   by mainstream libraries

   :param source_path: str path to source
   :param destination_path: str path to save to without format
   :param format: intended format without ., e.g. wav
   """
    export_path = destination_path+"."+format
    sound = AudioSegment.from_file(
        source_path,
        codec="opus"
    ).export(export_path, format=format)
    return export_path