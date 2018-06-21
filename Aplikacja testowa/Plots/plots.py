import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import rfft, rfftfreq


def plot_raw_signal(signal):
    """plot signal over time"""
    plt.title('Signal Wave')
    plt.xlabel('time (s)')
    plt.ylabel('aplitude')
    plt.plot(np.arange(len(signal)),signal)
    plt.show()

def plot_spectrum(signal, samplerate):
    """plot spectrum of given signal using FFT"""
    n = len(signal)
    d = 1/samplerate
    hs = np.absolute(rfft(signal))
    fs = rfftfreq(n,d)
    print(hs)
    plt.title('Spectrum')
    plt.xlabel('frequency (Hz)')
    plt.ylabel('aplitude')
    plt.plot(fs, hs, 'r')
    plt.show()

def plot_mel_scale():
    """ pass """
    pass
