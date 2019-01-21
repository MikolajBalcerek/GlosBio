import os
import unittest
from pathlib import Path

from plots.spectrogram_plot import *


class TestSpectrogramPlotting(unittest.TestCase):
    """ Unit tests for plotting and saving spectrogram plots """

    @classmethod
    def setUpClass(cls):
        cls.AUDIO_1_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "1.wav")
        cls.DIRECTORY_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)))


    def test_plot_spectrogram_pdf_success(self):
        """
        for pdf plot
        create a plot in memory from test audio
        """
        plot_bytesIO = plot_save_spectrogram_BytesIO(self.AUDIO_1_PATH, self.DIRECTORY_TEST, "pdf")

        # test assertion in-memory plot when saved is of the same size as expected
        good_plot_path_pdf = f"{self.DIRECTORY_TEST}/plot_spectrogram_pdf.pdf"
        test_in_memory_plot_path = f"{self.DIRECTORY_TEST}/test_plot_spectrogram_pdf.pdf"

        with open(test_in_memory_plot_path, "wb") as file:
            file.write(plot_bytesIO.getvalue())

        self.assertEqual(os.path.getsize(good_plot_path_pdf),
                         os.path.getsize(test_in_memory_plot_path),
                         "Generated spectrogram plot PDF file from memory when "
                         "saved differs in size from a known good one")

        # clear up the test file
        os.remove(test_in_memory_plot_path)

    def test_plot_spectrogram_png_success(self):
        """
        for png plot
        create a plot in memory from test audio
        """
        plot_bytesIO = plot_save_spectrogram_BytesIO(self.AUDIO_1_PATH, self.DIRECTORY_TEST, "png")

        # test assertion in-memory plot when saved is of the same size as expected
        good_plot_path_pdf = f"{self.DIRECTORY_TEST}/plot_spectrogram_png.png"
        test_in_memory_plot_path = f"{self.DIRECTORY_TEST}/test_plot_spectrogram_png.png"

        with open(test_in_memory_plot_path, "wb") as file:
            file.write(plot_bytesIO.getvalue())

        self.assertEqual(os.path.getsize(good_plot_path_pdf),
                         os.path.getsize(test_in_memory_plot_path),
                         "Generated spectrogram plot PDF file from memory when "
                         "saved differs in size from a known good one")

        # clear up the test file
        os.remove(test_in_memory_plot_path)

if __name__ == '__main__':
    unittest.main()
