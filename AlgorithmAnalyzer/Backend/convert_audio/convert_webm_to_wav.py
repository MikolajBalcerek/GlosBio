from pydub import AudioSegment

# this requires you to have http://ffmpeg.org/ installed
# and ADDED TO YOUR PATH


def convert_webm_to_wav(source_path : str, destination_path: str):
    """
    Converts webm from a given path to wav
    :param source_path: string to path source file in webm format
    :param destination_path: string path for desired outcome in flac format
    """
    sound = AudioSegment.from_file(
        source_path,
        codec="opus"
    ).export(destination_path, format="wav")