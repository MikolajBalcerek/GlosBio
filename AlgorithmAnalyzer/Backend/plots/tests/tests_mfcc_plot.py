import os
import unittest

from plots.mfcc_plot import _plot_mfcc_color_boxes, plot_save_mfcc_color_boxes


class TestMfccPlotting(unittest.TestCase):
    def setUp(self):

        self.AUDIO_1_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "1.wav")
        self.DIRECTORY_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)))

    # unit test for plotting and saving figure
    def test_plot_save_mfcc_color_boxed_pdf_success(self):
        # create a plot from test audio and save it
        plot_save_mfcc_color_boxes(self.AUDIO_1_PATH, self.DIRECTORY_TEST,
                                   "test_plot_mfcc_pdf", "pdf")

        test_plot_path = f"{self.DIRECTORY_TEST}/test_plot_mfcc_pdf.pdf"
        good_plot_path = f"{self.DIRECTORY_TEST}/plot_mfcc_pdf.pdf"

        # test assertion contents
        self.assertEqual(os.path.getsize(test_plot_path), os.path.getsize(good_plot_path),
                         "Generated MFCC plot PDF file size differs from a known good one")

        # clear up the test file
        os.remove(test_plot_path)


    # def test_plot_save_mfcc_color_boxed_success_png(self):
    #     plot_save_mfcc_color_boxes(self.DIRECTORY_TEST, "test_mfcc_plot", "pdf")
    #
    #
    # def test_plot_save_mfcc_color_boxed_failure_extension(self):
    #     plot_save_mfcc_color_boxes(self.DIRECTORY_TEST, "test_mfcc_plot", "pdf")
    #

if __name__ == '__main__':
    unittest.main()
