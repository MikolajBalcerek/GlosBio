from io import BytesIO
from typing import Tuple

import matplotlib.pyplot as plt

# This file holds helper functions that save plots from different packages


def save_matplotlib_figure(data: plt.Figure, file_name: str, saved_format: str = "png") -> BytesIO:
    """
    This function saves a matplotlib Figure object to a file

    :param data: matplotlib Figure object containing the plot
    :param directory_path: str path to the directory without the ending slash (/)
    :param file_name: name of the file (without the extension)
    :param saved_format: str type of plot image to be saved, png or pdf,
    defaults to pdf (vector format)

    :return file_path, file_io: str file_path to the saved file,
    BytesIO containing the requested plot
    """
    if saved_format == "png" or saved_format == "pdf":
        file_io = BytesIO()
        data.savefig(file_io, transparent=True, bbox_inches='tight',
                     format=saved_format)

        return file_io
    else:
        raise ValueError("Expected png or pdf as saved_format")
