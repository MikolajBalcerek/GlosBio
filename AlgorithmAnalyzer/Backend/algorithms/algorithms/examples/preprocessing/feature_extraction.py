import numpy as np
from scipy.fftpack import dct
import matplotlib.pyplot as plt

from .filters import preemphasis, get_window_func
from .preprocessing import normalize_signal_length


def _get_nfft(window_len):
    nfft = 1
    while nfft < window_len:
        nfft *= 2
    return nfft


def frame_signal(signal, window_len, step_len, num_steps, window_func):
    padding_len = num_steps * step_len + window_len
    signal = normalize_signal_length(signal, padding_len)
    # make len(signal) whole multiple of window_len
    indices = np.tile(np.arange(0, window_len), (num_steps, 1)) + \
        np.tile(np.arange(0, num_steps * step_len, step_len), (window_len, 1)).T
    indices = np.array(indices, np.int32)
    frames = signal[indices.astype(np.int32, copy=False)]
    window = get_window_func(window_func)(window_len)
    windows = np.tile(window, (len(frames), 1)).astype(frames.dtype)
    return frames * windows


def hz_to_mel(hz):
    return 2595 * np.log10(1 + hz / 700.)


def mel_to_hz(mel):
    return 700 * (10 ** (mel / 2595.) - 1)


def get_mel_filters(num_filters, sample_rate, nfft=512, low_freq=0, high_freq=None):
    high_freq = high_freq or sample_rate / 2
    low_mel = hz_to_mel(low_freq)
    high_mel = hz_to_mel(high_freq)
    mel_points = np.linspace(low_mel, high_mel, num_filters + 2)
    vertices = np.floor((nfft + 1) * mel_to_hz(mel_points) / sample_rate)
    # vertives of triangular mel filters

    filters = np.zeros((num_filters, int(np.floor(nfft / 2 + 1))))
    for mid in range(1, num_filters + 1):
        l, c, r = int(vertices[mid - 1]), int(vertices[mid]), int(vertices[mid + 1])
        # l, c, r - left, center, right vertieces

        # filters[mid - 1, :] is a triangular mel filter with vertices l, c, r
        for k in range(l, c):
            filters[mid - 1, k] = (k - vertices[mid - 1]) / (vertices[mid] - vertices[mid - 1])
        for k in range(c, r):
            filters[mid - 1, k] = (vertices[mid + 1] - k) / (vertices[mid + 1] - vertices[mid])

    return filters


def get_power_spectrum(signal, window_length=None, nfft=512):
    nfft = _get_nfft(window_length) if window_length else nfft
    spec = np.absolute(np.fft.rfft(signal, nfft))
    return ((1. / nfft) * ((spec) ** 2))


def apply_sine_lifter(matrix, lifter_length=22):
    _, cols = matrix.shape
    n = np.arange(cols)
    lift = 1 + (lifter_length / 2) * np.sin(np.pi * n / lifter_length)
    return matrix * lift


def get_mfccs(
    signal, rate, num_vectors=13, num_filters=26, padding_length=None,
    normalize_filter_banks=True, normalize_mfccs=True, apply_preemhasis=True, apply_lifter=True,
    window_length=.02, window_overlap=.01, window_func='hamming'
):
    padding_len = rate * padding_length if padding_length else len(signal)
    window_len = round(window_length * rate)
    step_len = round((window_length - window_overlap) * rate)
    num_steps = int(np.ceil(float(np.abs(padding_len - window_len)) / step_len))

    if apply_preemhasis:
        signal = preemphasis(signal)

    frames = frame_signal(signal, window_len, step_len, num_steps, window_func)

    nfft = _get_nfft(window_len)
    pow_specs = get_power_spectrum(frames, nfft=nfft)

    mel_filters = get_mel_filters(num_filters, rate, nfft=nfft)

    filtered = np.dot(pow_specs, mel_filters.T)
    filtered = np.where(filtered == 0, np.finfo(float).eps, filtered)
    log_filtered = 20 * np.log10(filtered)

    if normalize_filter_banks:
        log_filtered -= (np.mean(log_filtered, axis=0) + 10**-8)

    mfcc = dct(log_filtered, type=2, axis=1, norm='ortho')[:, 1: (num_vectors + 1)]
    if apply_lifter:
        mfcc = apply_sine_lifter(mfcc)
    if normalize_mfccs:
        mfcc -= (np.mean(mfcc, axis=0) + 10**-8)
    return mfcc


def _plot_mel_filters(sample_rate, num_filters=13, nfft=512):
    filters = get_mel_filters(
        num_filters, sample_rate, nfft=nfft, num_filters=num_filters
    )
    fig, ax = plt.subplots(figsize=(num_filters / 1.5, 4))
    ax.plot(np.arange(nfft / 2 + 1), filters.T)
    ax.set_title("Bank filtrów dla MFCC")
    ax.set_ylabel("Waga")
    ax.set_xlabel("Częstotliwość w melach")
    ax.set_ylim((.01, 1.01))
    plt.show()
