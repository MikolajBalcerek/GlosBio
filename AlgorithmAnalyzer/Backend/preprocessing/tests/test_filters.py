import os
import unittest

from scipy.io import wavfile
from ddt import ddt, data
import preprocessing.filters as filters


@ddt
class TestFilters(unittest.TestCase):
    def setUp(self):
        self.path = os.path.dirname(__file__)
        self.sig1_sr, sig1_stereo = wavfile.read(
            os.path.join(self.path, 'freesound.wav')
        )
        self.sig1 = sig1_stereo[:, 0]  # 1st channel

    def test_moving_average_lpf(self):
        cut_off = 50
        filtered = filters.moving_average_lpf(self.sig1, self.sig1_sr, cut_off)
        filtered = filtered.astype(self.sig1.dtype)
        wavfile.write(
            os.path.join(self.path, './data/moving_avg.wav'),
            self.sig1_sr, filtered
        )

    @data(
        'triangular',
        'sine',
        'blackman',
        'hann',
        'hamming',
        'blackmanharris'
    )
    def test_window(self, window_name):
        window_size = 500
        window = filters.get_window_func(window_name)(window_size)
        self.assertEqual(window.shape[0], window_size)

    @data(
        'triangular',
        'sine',
        'blackman',
        'hann',
        'hamming',
        'blackmanharris'
    )
    def test_fir_lowpass(self, window_name):
        cut_off = 800
        window = filters.get_window_func(window_name)
        filtered = filters.fir_lowpass(
            self.sig1, self.sig1_sr, cut_off, 200, window
        )
        filtered = filtered.astype(self.sig1.dtype)
        wavfile.write(
            os.path.join(self.path, './data/lpf_' + window_name + '.wav'),
            self.sig1_sr, filtered
        )

    @data(
        'triangular',
        'sine',
        'blackman',
        'hann',
        'hamming',
        'blackmanharris'
    )
    def test_fir_highpass(self, window_name):
        cut_off = 800
        window = filters.get_window_func(window_name)
        filtered = filters.fir_highpass(
            self.sig1, self.sig1_sr, cut_off, 200, window
        )
        filtered = filtered.astype(self.sig1.dtype)
        wavfile.write(
            os.path.join(self.path, './data/hpf_' + window_name + '.wav'),
            self.sig1_sr, filtered
        )

    @data(
        'triangular',
        'sine',
        'blackman',
        'hann',
        'hamming',
        'blackmanharris'
    )
    def test_fir_bandpass(self, window_name):
        high_cut_off = 1100
        low_cut_off = 700
        window = filters.get_window_func(window_name)
        filtered = filters.fir_bandpass(
            self.sig1, self.sig1_sr, low_cut_off, high_cut_off, 50, window
        )
        filtered = filtered.astype(self.sig1.dtype)
        wavfile.write(
            os.path.join(self.path, './data/bpf_' + window_name + '.wav'),
            self.sig1_sr, filtered
        )

    @data(
        'triangular',
        'sine',
        'blackman',
        'hann',
        'hamming',
        'blackmanharris'
    )
    def test_fir_bandstop(self, window_name):
        high_cut_off = 1100
        low_cut_off = 700
        window = filters.get_window_func(window_name)
        filtered = filters.fir_bandstop(
            self.sig1, self.sig1_sr, low_cut_off, high_cut_off, 50, window
        )
        filtered = filtered.astype(self.sig1.dtype)
        wavfile.write(
            os.path.join(self.path, './data/bsf_' + window_name + '.wav'),
            self.sig1_sr, filtered
        )
