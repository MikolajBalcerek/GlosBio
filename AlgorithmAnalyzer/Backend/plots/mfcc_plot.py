import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
import scipy.io.wavfile as wav
from python_speech_features import mfcc

# this file handles plotting and saving mfcc plots


def plot_mfcc_feat_lines():
    (rate, sig) = wav.read("1.wav")
    mfcc_feat = mfcc(sig, rate)
    fig = plt.figure(figsize=(10,10))
    return fig


def plot_mfcc_data_boxes():
    (rate, sig) = wav.read("1.wav")
    mfcc_feat = mfcc(sig, rate)
    fig, ax = plt.subplots()
    mfcc_data = np.swapaxes(mfcc_feat, 0, 1)
    cax = ax.imshow(mfcc_data, interpolation='nearest', cmap=cm.coolwarm,
                    origin='lower', aspect='auto')

    return fig



def save_matplotlib_plot(data, title=None, saved_format: str="pdf"):
    """

    :param size_inches: int size in inches of the plot to be created, 5 -> 5x5
    :param saved_format: str type of plot image to be saved, png or pdf
    :return:
    """
    data.savefig(f'fo474o.png', transparent= True, bbox_inches='tight')

if __name__ == "__main__":
    mfcc_data = plot_mfcc_data_boxes();
    save_matplotlib_plot(mfcc_data)