from contextlib import suppress

import speech_recognition as sr
from Backend import secret_keys


#this file handles speech to text

def recognize_speech(audio_file : sr.AudioFile, language="pl-PL"):
    """
    speech to text from the audio_file in sr.AudioFile

    :param audio_file: sr.AudioFile format, init by sr.AudioFile(path : str)
    :param language: language in the "pl-PL" style, default polish
    :return: string of recognized text
    """

    r = sr.Recognizer()
    # converting to audioData

    audio = r.record(audio_file)
    try:
        # GOOGLE
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        return r.recognize_google(audio, language="pl-PL")
    except:
        # BING
        #TODO: NEW API KEY
        with suppress(Exception):
            return r.recognize_bing(audio, key=secret_keys.SECRET_BING_KEY,
                                    language="pl-PL")
        print("BING api key is outdated")
        return None


def recognize_speech_from_path(path : str, language="pl-PL"):
    """
    speech to text from the file under string path(preferred .wav)

    :param path: str full path to the audiofile
    :param language: language in the "pl-PL" style, default polish
    :return: string of recognized text
    """
    # recognize speech
    with sr.AudioFile(path) as _file:
        recognized_speech = recognize_speech(_file)
    return recognized_speech
