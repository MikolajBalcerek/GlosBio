import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import soundfile

#THIS USES SOUNDDEVICE LIBRARY
#CONTRATY TO SPEECH RECOGNITION, WHICH USES pyAudio

###This file here only handles simple recordings on demand###

sd.default.samplerate = 44100
sd.default.channels = 2


def record_for_time(seconds : float):
    """
    this function will record for seconds number time with set default frequency
    :param seconds float
    :return Numpy Array of float32 type:
    """
    myrecording = sd.rec(seconds * sd.default.samplerate, blocking=True)
    return myrecording


def play_from_file(file):
    data, fs = soundfile.read(file)
    sd.play(data, fs, device=sd.default.device)
    status = sd.wait()

if __name__ == "__main__":
    ### Przykład użycia ###
    ###nagranie 5s i puszczenie###
    recording = record_for_time(5)
    sd.play(recording)
    sd.wait()
