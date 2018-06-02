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