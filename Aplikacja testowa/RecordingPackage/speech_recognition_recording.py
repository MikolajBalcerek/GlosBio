import speech_recognition as sr
import io
import soundfile
#This file handles smart voice recording

def record_till_end_of_voice():
    """
    this records audio until significant noise has begun and ended
    :return: AudioData
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("LOG: adjusting for noise...")
        r.adjust_for_ambient_noise(source)
        print("LOG: recording...")
        audio = r.listen(source)
    return audio, r


def recognize_speech(AudioData : sr.AudioData, Recognizer : sr.Recognizer):
    r = Recognizer
    audio = AudioData
    #try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
    return r.recognize_google(audio, language="pl-PL")
    # except sr.UnknownValueError:
    #     print("Google Speech Recognition could not understand audio")
    # except sr.RequestError as e:
    #     print("Could not request results from Google Speech Recognition service; {0}".format(e))

def record_and_recognize():
    """
    Records voice and return AudioData and string with recognized text
    :return Audiodata, str recognized Text
    """
    AudioData, Recognizer = record_till_end_of_voice()
    return AudioData, str(recognize_speech(AudioData, Recognizer))

def convert_AudioData_to_Numpy_array_and_fs(AudioData : sr.AudioData):
    """
    this converts AudioData from speech_recognition to Numpy Array and fs int that is used by
    our own simple_audio, and external soundfile, sounddevice
    :param AudioData:
    :return:
    """
    flac = io.BytesIO(AudioData.get_flac_data())
    data, fs = soundfile.read(flac)
    return {"NumpyArray" : data, "fs" : fs}