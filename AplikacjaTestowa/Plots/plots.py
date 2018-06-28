import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import rfft, rfftfreq
from scipy import signal

def plot_raw_signal(sig):
    """ plot signal over time """
    plt.title('Signal Wave')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.plot(np.arange(len(sig)),signal)
    plt.show()

def plot_spectogram(sig, samplerate):
    """-"""
    f, t, Sxx = signal.spectrogram(sig, samplerate)
    plt.pcolormesh(t, f, Sxx)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
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

def basic_plots(sig, samplerate):
    plt.figure(1)
    plt.subplot(211)
    plt.title('Signal Wave')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.plot(np.arange(len(sig)),sig)

    plt.subplot(212)
    plt.title('Spectogram')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    f, t, Sxx = signal.spectrogram(sig, samplerate, nperseg=1024)
    # plt.ylim(5000)
    plt.pcolormesh(t, f, Sxx)
    #
    plt.show()
