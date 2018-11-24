import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
import scipy.io.wavfile as wav
from python_speech_features import mfcc

from plots.save_plot import save_matplotlib_figure

# this file handles plotting and saving mfcc plots


def _plot_mfcc_color_boxes(audio_path: str) -> plt.Figure:
    """
    Plots a MFCC figure from an audio file (wav) under audio_path

    :param audio_path: str full path to audio file
    :return: plt.Figure containing the MFCC colored boxes plot
    """
    (rate, sig) = wav.read(audio_path)
    mfcc_features_lines = mfcc(sig, rate, nfft=1250)
    figure, axis = plt.subplots()
    mfcc_data = np.swapaxes(mfcc_features_lines, 0, 1)
    axis.set_title("MFCC")
    format_figure = axis.imshow(mfcc_data, interpolation='nearest', cmap=cm.coolwarm,
                    origin='lower', aspect='auto')

    return figure


def plot_save_mfcc_color_boxes(audio_path: str, directory_path: str,
                               file_name: str, saved_format: str = "pdf"):
    """
    Creates a MFCC colored boxes plot and saves it to provided path
    with the given name and format (pdf or png)

    :param audio_path: str full path to audio file
    :param directory_path: str path to the directory without the ending slash (/)
    :param file_name: name of the file (without the extension)
    :param saved_format: str type of plot image to be saved, png or pdf,
    defaults to pdf (vector format)
    """
    figure = _plot_mfcc_color_boxes(audio_path)
    save_matplotlib_figure(figure, directory_path, file_name, saved_format)

