import speech_recognition as sr
import io
import soundfile
#This file handles smart voice recording

def record_till_end_of_voice(vc):
    """
    this records audio until significant noise has begun and ended
    :return: AudioData
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        vc.view.setKom1Text("LOG: adjusting for noise...")
        vc.parent.update()
        r.adjust_for_ambient_noise(source)
        vc.view.setKom2Text("LOG: recording...")
        vc.parent.update()
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
