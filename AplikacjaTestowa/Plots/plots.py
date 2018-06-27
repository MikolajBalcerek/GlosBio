import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import rfft, rfftfreq

class Spectrum:
    def __init__(self, hs, fs, framerate):
        self.hs = np.asarray(hs)
        self.fs = np.asarray(fs)
        self.framerate = framerate

    def plot(self):
        plt.plot(self.fs, self.hs, 'r')
        plt.show()


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

def plot_spectogram(signal, samplerate, segment_length):
    """-"""
    window = np.hamming(segment_length)
    ys = signal.copy()
    ts = np.linspace(len(ys))
    i = 0
    j = segment_length
    step = segment_length / 2

    spec_map = {}

    while j < len(ys):
        segment_ys = ys[i:j].copy()
        segment_ys *= window
        temp_ts = ts[i:j].copy()
        segment_ts = np.linspace(len(temp_ts))

        temp_fft_hs = np.fft.rfft(self.ys)
        temp_fft_fs = np.fft.rfftfreq(len(segment_ys), 1 / samplerate)

        t = (temp_ts[0] + temp_ts[-1]) / 2

        spec_map[t] = Spectrum(temp_fft_hs, temp_fft_hs, samplerate)
        spec_map[t].plot()

        i += step
        j += step
