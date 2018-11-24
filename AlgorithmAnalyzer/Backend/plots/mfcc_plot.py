import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
import scipy.io.wavfile as wav
from python_speech_features import mfcc

# this plots MFCC
self, username, set_type="train", filetype="wav", no_file_type=False
def plot_mfcc(username, set_type, filetype):
    (rate,sig) = wav.read("1.wav")
    mfcc_feat = mfcc(sig,rate)

    ig, ax = plt.subplots()
    mfcc_data= np.swapaxes(mfcc_feat, 0 ,1)
    cax = ax.imshow(mfcc_data, interpolation='nearest', cmap=cm.coolwarm, origin='lower', aspect='auto')
    ax.set_title('MFCC')
    #Showing mfcc_data
    plt.show()
    #Showing mfcc_feat
    plt.plot(mfcc_feat)
    plt.show()

