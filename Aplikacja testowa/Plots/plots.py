import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import rfft, rfftfreq


def plot_raw_signal(signal):
    """ plot signal over time """
    plt.title('Signal Wave')
    plt.xlabel('time')
    plt.ylabel('aplitude')
    plt.plot(np.arange(len(signal)),signal)
    plt.show()

def plot_spectrum(signal, samplerate):
    """ plot spectrum of given signal using FFT """
    n = len(signal)
    # d = 1/samplerate
    hs = np.absolute(rfft(signal))
    fs = rfftfreq(n)
    plt.title('Spectrum')
    plt.xlabel('frequency (Hz)')
    plt.ylabel('aplitude')
    plt.plot(fs, hs, 'r')
    plt.show()

def plot_mel_scale():
    """ plot Mel scale to Hertz scale ratio """
    fs = np.arange(20000)
    ms = 2595 * np.log10(1 + fs/700)
    plt.title('Mel/Hz ratio')
    plt.xlabel('Hertz scale')
    plt.ylabel('Mel scale')
    plt.plot(fs,ms)
    plt.grid(True)
    plt.show()
    pass
