import os
import unittest
from pathlib import Path

from plots.mfcc_plot import _plot_mfcc_color_boxes, plot_save_mfcc_color_boxes_BytesIO


class TestMfccPlotting(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.AUDIO_1_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "1.wav")
        self.DIRECTORY_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)))

    # unit tests for plotting and saving figure

    # for pdf plot
    def test_plot_save_mfcc_color_boxed_pdf_success(self):
        # create a plot from test audio and save it
        file_path, plot_bytesIO = plot_save_mfcc_color_boxes_BytesIO(self.AUDIO_1_PATH, self.DIRECTORY_TEST,
                                   "test_plot_mfcc_pdf", "pdf")

        test_plot_path = f"{self.DIRECTORY_TEST}/test_plot_mfcc_pdf.pdf"
        good_plot_path = f"{self.DIRECTORY_TEST}/plot_mfcc_pdf.pdf"

        # test assertion file_path as expected
        self.assertEqual(test_plot_path, file_path, "File path for the pdf MFCC"
                                                    "plot different than expected")

        # test assertion saved file size is the same as expected
        self.assertEqual(os.path.getsize(test_plot_path), os.path.getsize(good_plot_path),
                         "Generated MFCC plot PDF file size differs from a known good one")


        # test assertion in-memory plot when saved is of the same size as expected
        test_in_memory_plot_path = f"{self.DIRECTORY_TEST}/test_in_memory_plot_mfcc_pdf.pdf"
        # save in-memory plot to file - decided to do this the following way
        # as comparing file from memory to saved one results from meta-data bytes differing
        with open(test_in_memory_plot_path, "wb") as file:
            file.write(plot_bytesIO.getvalue())

        self.assertEqual(os.path.getsize(good_plot_path),
                         os.path.getsize(test_in_memory_plot_path),
                         "Generated MFCC plot PDF file from memory when saved differs in size from a known good one")

        # clear up the test file
        os.remove(test_plot_path)
        os.remove(test_in_memory_plot_path)

    # for png plot
    def test_plot_save_mfcc_color_boxed_success_png(self):
        # create a plot from test audio and save it
        file_path, plot_bytesIO = plot_save_mfcc_color_boxes_BytesIO(self.AUDIO_1_PATH, self.DIRECTORY_TEST,
                                   "test_plot_mfcc_png", "png")

        test_plot_path = f"{self.DIRECTORY_TEST}/test_plot_mfcc_png.png"
        good_plot_path = f"{self.DIRECTORY_TEST}/plot_mfcc_png.png"

        # test assertion contents
        self.assertEqual(os.path.getsize(test_plot_path), os.path.getsize(good_plot_path),
                         "Generated MFCC plot PNG file size differs from a known good one")

        # test assertion file_path as expected
        self.assertEqual(test_plot_path, file_path, "File path for the png MFCC"
                                                    "plot different than expected")


        # test assertion in-memory plot when saved is of the same size as expected
        test_in_memory_plot_path = f"{self.DIRECTORY_TEST}/test_in_memory_plot_mfcc_png.png"
        # save in-memory plot to file - decided to do this the following way
        # as comparing file from memory to saved one results from meta-data bytes differing
        with open(test_in_memory_plot_path, "wb") as file:
            file.write(plot_bytesIO.getvalue())

        self.assertEqual(os.path.getsize(good_plot_path),
                         os.path.getsize(test_in_memory_plot_path),
                         "Generated MFCC plot PNG file from memory when saved differs in size from a known good one")

        # clear up the test file
        os.remove(test_plot_path)
        os.remove(test_in_memory_plot_path)

    # check for exception for bad extension
    def test_plot_save_mfcc_color_boxed_fail_wrong_extension_exception(self):
        # check if the exception was thrown
        with self.assertRaises(ValueError, msg="No or bad exception thrown"
                                               "for .wav output for a mfcc plot"):
            file_path = plot_save_mfcc_color_boxes_BytesIO(self.AUDIO_1_PATH, self.DIRECTORY_TEST,
                                   "test_plot_mfcc_wav", "wav")

    def test_plot_save_mfcc_color_boxed_fail_wrong_extension_file_exists(self):
        # check for side effects of failing saving the file due to wrong extension
        file_path = None
        file_bytesIO = None
        try:
            file_path, file_bytesIO = plot_save_mfcc_color_boxes_BytesIO(self.AUDIO_1_PATH,
                                                                         self.DIRECTORY_TEST,
                                                   "test_plot_mfcc_wav", "wav")
        except ValueError:
            pass
        finally:
            # check for returned Path
            self.assertIs(file_path, None, "Unexpected file_path was returned,"
                                               "expected None")


            # check if no file was created
            test_plot_path = f"{self.DIRECTORY_TEST}/test_plot_mfcc_wav.wav"
            self.assertFalse(Path(test_plot_path).is_file(), f"A file was created,"
                            "or exists of {test_plot_path} -> plot with wav extension!")

            # check if No BytesIO object was returned
            self.assertIs(file_bytesIO, None, msg="Plot's bytesIO was returned when it should be empty")









if __name__ == '__main__':
    unittest.main()
