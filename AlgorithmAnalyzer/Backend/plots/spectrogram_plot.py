from io import BytesIO

import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
from scipy import signal

from plots.save_plot import save_matplotlib_figure

# this file handles plotting and saving spectrogram plots


def _plot_spectrogram_from_bytes(audio_bytes: bytes) -> plt.Figure:
    """
    Plots a spectrogram figure from an audio file (wav) under audio_path

    :param audio_bytes: bytes containing wav file audio
    :return: plt.Figure containing the spectogram
    """
    (rate, signal) = wav.read(audio_bytes)
    plt.specgram(signal, Fs=rate)
    plt.autoscale()
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.title("Spectrogram")
    figure = plt.figure(plt.get_fignums()[0], aspect='auto')
    return figure


def plot_save_spectrogram_BytesIO(file_bytes: bytes,
                                  file_name: str, saved_format: str = "pdf") -> BytesIO:
    """
    Creates a spectrogram and saves it to a BytesIO object
    with the given name and format (pdf or png)

    :param file_bytes: bytes containing wav file audio
    :param file_name: name of the file (without the extension)
    :param saved_format: str type of plot image to be saved, png or pdf,
    defaults to pdf (vector format)
    :return file_io: BytesIO containing the requested plot
    """
    figure = _plot_spectrogram_from_bytes(file_bytes)
    file_io = save_matplotlib_figure(figure, file_name, saved_format)
    return file_io
