import speech_recognition as sr
import sys
from GlosBio.AlgorithmAnalyzer.Backend import secret_keys


#this file handles speech to text

def recognize_speech(audio_file : sr.AudioFile, language="pl-PL"):
    """
    speech to text from the audio_file

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
        print("BING api key is outdated")
        return r.recognize_bing(audio, key=secret_keys.SECRET_BING_KEY,
                                language="pl-PL")
