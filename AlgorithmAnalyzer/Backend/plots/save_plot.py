import matplotlib.pyplot as plt

# This file holds helper functions that save plots from different packages


def save_matplotlib_figure(data: plt.Figure, directory_path: str,
                           file_name: str, saved_format: str = "png") -> str:
    """
    This function saves a matplotlib Figure object to a file

    :param data: matplotlib Figure object containing the plot
    :param directory_path: str path to the directory without the ending slash (/)
    :param file_name: name of the file (without the extension)
    :param saved_format: str type of plot image to be saved, png or pdf,
    defaults to pdf (vector format)

    :return file_path: str file_path to the saved file
    """
    if saved_format == "png" or saved_format == "pdf":
        file_path = f'{directory_path}/{file_name}.{saved_format}'
        data.savefig(file_path,
                     transparent=True, bbox_inches='tight')
        return file_path
    else:
        raise ValueError("Expected png or pdf as saved_format")
