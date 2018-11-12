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


def triangular_window(window_size):
    return 1 - np.abs(2 * np.arange(window_size) / (window_size - 1) - 1)


def sine_window(window_size):
    return np.sin(math.pi * np.arange(window_size) / (window_size - 1))


def cosine_window(window_size, alpha):
    return alpha - (1 - alpha) * \
        np.cos(2 * math.pi * np.arange(window_size) / (window_size - 1))


def hann_window(window_size):
    return cosine_window(window_size, alpha=.5)


def hammiong_window(window_size):
    return cosine_window(window_size, alpha=0.53836)


def blackman_window(window_size):
    return np.blackman(window_size)


def blackmanharris_window(window_size):
    xs = math.pi * np.arange(window_size) / (window_size - 1)
    a, b, c, d = .35875, .48829, .14128, .01168
    return a - b * np.cos(2 * xs) + c * np.cos(4 * xs) - d * np.cos(6 * xs)


def get_window_func(name):
    return {
        'triangular': triangular_window,
        'sine': sine_window,
        'cosine': cosine_window,
        'hann': hann_window,
        'hamming': hammiong_window,
        'blackman': blackman_window,
        'blackmanharris': blackmanharris_window
    }[name]


def fir_window_size(relative_transition_band):
    N = int(np.ceil(4. / relative_transition_band))
    if N % 2 == 0:
        N += 1
    return N


def sinc_filter(size, relative_cut_off):
    return np.sinc(2 * relative_cut_off * (np.arange(size) - size // 2))


def fir_lpf_coeffs(window_func, relative_cut_off, window_size):
    shifted_sinc = sinc_filter(window_size, relative_cut_off)
    window = window_func(window_size)
    windowed_sinc = shifted_sinc * window
    return windowed_sinc / np.sum(windowed_sinc)


def fir_hpf_coeffs(window_func, relative_cut_off, window_size):
    coeffs = - fir_lpf_coeffs(window_func, relative_cut_off, window_size)
    coeffs[window_size // 2] += 1
    return coeffs


def fir_lowpass(signal, sample_rate, cut_off, transition_band,
                window_func=blackman_window, window_size=None):
    rel_cut_off = 1. * cut_off / sample_rate
    rel_transition_band = 1. * transition_band / sample_rate
    N = window_size if window_size else fir_window_size(rel_transition_band)
    return np.convolve(signal, fir_lpf_coeffs(window_func, rel_cut_off, N))


def fir_highpass(signal, sample_rate, cut_off, transition_band,
                 window_func=blackman_window, window_size=None):
    rel_cut_off = 1. * cut_off / sample_rate
    rel_transition_band = 1. * transition_band / sample_rate
    N = window_size if window_size else fir_window_size(rel_transition_band)
    return np.convolve(signal, fir_hpf_coeffs(window_func, rel_cut_off, N))


def fir_bandpass(signal, sample_rate, left_freq, right_freq, transition_band,
                 window_func=blackman_window, window_size=None):
    rel_left = 1. * left_freq / sample_rate
    rel_right = 1. * right_freq / sample_rate
    rel_transition_band = 1. * transition_band / sample_rate
    N = window_size if window_size else fir_window_size(rel_transition_band)
    right_lpf_coeffs = fir_lpf_coeffs(window_func, rel_right, N)
    left_hpf_coeffs = fir_hpf_coeffs(window_func, rel_left, N)
    coeffs = np.convolve(left_hpf_coeffs, right_lpf_coeffs)
    return np.convolve(signal, coeffs)


def fir_bandstop(signal, sample_rate, left_freq, right_freq, transition_band,
                 window_func=blackman_window, window_size=None):
    rel_left = 1. * left_freq / sample_rate
    rel_right = 1. * right_freq / sample_rate
    rel_transition_band = 1. * transition_band / sample_rate
    N = window_size if window_size else fir_window_size(rel_transition_band)
    right_hpf_coeffs = fir_hpf_coeffs(window_func, rel_right, N)
    left_lpf_coeffs = fir_lpf_coeffs(window_func, rel_left, N)
    coeffs = left_lpf_coeffs + right_hpf_coeffs
    return np.convolve(signal, coeffs)


def better_window_size(name, sr, transition_band):
        return {
            'hamming': 8 * math.pi * sr / transition_band + 1,
            'hann': 8 * math.pi * sr / transition_band + 1,
            'triangular': 8 * math.pi * sr / transition_band + 1
        }[name]
