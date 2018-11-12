import math

import numpy as np


def preemphasis(signal, alpha=.95):
    return np.append(signal[0], signal[1:] - alpha * signal[:-1])


def moving_average(sequence, N):
    sums = np.cumsum(sequence)
    shifted = np.insert(sums, 0, 0)
    window_sums = (shifted[N:] - shifted[:-N])
    return window_sums / N


def moving_average_lpf(signal, sample_rate, cut_off):
    ratio = cut_off / sample_rate
    window_size = int(math.sqrt(.196202 + ratio**2) / ratio)
    return moving_average(signal, window_size)


def moving_average_hpf(signal, sample_rate, cut_off):
    return signal - moving_average_lpf(signal, sample_rate, cut_off)


def blackman_window_size(sample_rate, transition_band):
    N = int(np.ceil(4. * sample_rate / transition_band))
    if N % 2 == 0:
        N += 1
    return N

def sinc_blackman_coeffs(sample_rate, cut_off, transition_band):
    freq_ratio = 1. * cut_off / sample_rate
    N = blackman_window_size(sample_rate, transition_band)
    middle = (N - 1.) / 2
    shifted_sinc = np.sinc(2 * freq_ratio * (np.arange(N) - middle))
    blackman_window = np.blackman(N)

    windowed_sinc = shifted_sinc * blackman_window
    return windowed_sinc / np.sum(windowed_sinc)


def sinc_blackman_lpf(sample, sample_rate, cut_off, transition_band):
    return np.convolve(
        sample,
        sinc_blackman_coeffs(sample_rate, cut_off, transition_band)
    )


def sinc_blackman_hpf(sample, sample_rate, cut_off, transition_band):
    N = blackman_window_size(sample_rate, transition_band)
    middle = (N - 1.) / 2
    h = - sinc_blackman_coeffs(sample_rate, cut_off, transition_band)
    h[middle] += 1
    return np.convolve(sample, h)
