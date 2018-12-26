from typing import Union
from io import BytesIO
from pydub import AudioSegment


def convert_webm_to_format(source: Union[BytesIO, str],
                           format: str = "wav", destination_path: str = None) -> Union[BytesIO, str]:
    """ Helper function converting webm to wav so it can be handled
   by mainstream libraries
   Works in memory from BytesIO object and returns bytesIO as well

   :param source: BytesIO object or str path to the source file
   :param format: intended format without ., e.g. wav
   :param destination_path: None for the file to be saved in memory as BytesIO,
   or str path to save to without format (e.g ~/tests/1)
   :returns: BytesIO object of the converted file or full str path
   where the file was saved, depending on destination_path value
   """

    if type(source) is BytesIO:
        export_file = BytesIO()
    elif type(source) is str:
        export_file = destination_path + "." + format
    else:
        raise TypeError("source given is of wrong type, should be BytesIO or str,"
                        f"is {type(source)}")

    sound = AudioSegment.from_file(
        source,
        codec="opus"
    ).export(export_file, format=format)

    return export_file

