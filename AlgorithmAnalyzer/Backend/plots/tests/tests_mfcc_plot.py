import os
import unittest

import matplotlib.pyplot as plt
from plots.mfcc_plot import plot_save_mfcc_color_boxes_BytesIO
from plots.save_plot import save_matplotlib_figure


class TestMfccPlotting(unittest.TestCase):
    """ Unit tests for plotting and saving MFCC plots """

    @classmethod
    def setUpClass(self):
        self.AUDIO_1_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "1.wav")
        self.DIRECTORY_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)))

    def test_plot_mfcc_color_boxed_pdf_success(self):
        """
        for pdf plot
        create a plot in memory from test audio
        """
        plot_bytesIO = plot_save_mfcc_color_boxes_BytesIO(self.AUDIO_1_PATH, self.DIRECTORY_TEST, "pdf")

        # test assertion in-memory plot when saved is of the same size as expected
        good_plot_path_pdf = f"{self.DIRECTORY_TEST}/plot_mfcc_pdf.pdf"
        test_in_memory_plot_path = f"{self.DIRECTORY_TEST}/test_plot_mfcc_pdf.pdf"

        with open(test_in_memory_plot_path, "wb") as file:
            file.write(plot_bytesIO.getvalue())

        self.assertEqual(os.path.getsize(good_plot_path_pdf),
                         os.path.getsize(test_in_memory_plot_path),
                         "Generated MFCC plot PDF file from memory when "
                         "saved differs in size from a known good one")

        # clear up the test file
        os.remove(test_in_memory_plot_path)

    def test_plot_mfcc_color_boxed_png_success(self):
        """
        for png plot
        create a plot in memory from test audio
        """
        plot_bytesIO = plot_save_mfcc_color_boxes_BytesIO(self.AUDIO_1_PATH, self.DIRECTORY_TEST, "png")

        # test assertion in-memory plot when saved is of the same size as expected
        good_plot_path_pdf = f"{self.DIRECTORY_TEST}/plot_mfcc_png.png"
        test_in_memory_plot_path = f"{self.DIRECTORY_TEST}/test_plot_mfcc_png.png"

        with open(test_in_memory_plot_path, "wb") as file:
            file.write(plot_bytesIO.getvalue())

        self.assertEqual(os.path.getsize(good_plot_path_pdf),
                         os.path.getsize(test_in_memory_plot_path),
                         "Generated mfcc plot PDF file from memory when "
                         "saved differs in size from a known good one")

        # clear up the test file
        os.remove(test_in_memory_plot_path)


    def test_plot_save_mfcc_color_boxed_fail_wrong_extension_exception(self):
        # check for exception for bad extension
        with self.assertRaises(ValueError, msg="No or bad exception thrown"
                                               "for .wav output for a mfcc plot"):
            file_IO = plot_save_mfcc_color_boxes_BytesIO(self.AUDIO_1_PATH, self.DIRECTORY_TEST, "wrong")

    def test_plot_save_matplot_figure_wrong_extension_exception(self):
        """ check for exception for bad extension in save_matplotlib_figure"""
        example_figure = plt.Figure()
        with self.assertRaises(ValueError, msg="No or bad exception thrown"
                                               "for .wav output for a mfcc plot"):
            file_IO = save_matplotlib_figure(example_figure, "some_bad_file", "wrong_extension")

if __name__ == '__main__':
    unittest.main()
