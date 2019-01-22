from io import BytesIO
from warnings import catch_warnings, simplefilter

import matplotlib.pyplot as plt
import scipy.io.wavfile as wav

from plots.save_plot import save_matplotlib_figure

# this file handles plotting and saving spectrogram plots


def _plot_spectrogram_from_bytes(audio_bytes: bytes) -> plt.Figure:
    """
    Plots a spectrogram figure from an audio file (wav) under audio_path

    :param audio_bytes: bytes containing wav file audio
    :return: plt.Figure containing the spectogram
    """
    (rate, signal) = wav.read(audio_bytes)
    plt.clf()
    with catch_warnings():
        simplefilter("ignore")
        # TODO: gives a RuntimeWarning: divide by zero encountered in log10
        #  Z = 10. * np.log10(spec)
        plt.specgram(signal, Fs=rate)

    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.title("Spectrogram")
    figure = plt.gcf()
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
