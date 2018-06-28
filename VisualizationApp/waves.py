import numpy as np
import python_speech_features as psf

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput, Select
from bokeh.plotting import figure
from bokeh.palettes import YlGn3

import load_data



_SPARSNESS = 3
_WINDOW_SCALING = 2
_BASE_FILE_NAME = load_data.get_file_names()[0]
_BASE_FILE = load_data.load_file(_BASE_FILE_NAME, _WINDOW_SCALING)
_BASE_FILE_RAW = load_data.load_raw_file(_BASE_FILE_NAME)


data_raw_signal = ColumnDataSource(data=
	dict(x=np.arange(0, _SPARSNESS*len(_BASE_FILE), step=_SPARSNESS), y=_BASE_FILE))

plot_raw_signal = figure(plot_height=400, plot_width=400, title="Raw signal",
              tools="crosshair,pan,reset,save,wheel_zoom")
              # ,x_range=[0, len(_BASE_FILE)], y_range=[min(_BASE_FILE), max(_BASE_FILE)])
plot_raw_signal.line('x', 'y', source=data_raw_signal, line_width=3, line_alpha=0.6)


data_mfcc = np.swapaxes(psf.mfcc(_BASE_FILE_RAW[1], _BASE_FILE_RAW[0]), 0, 1)
plot_mfcc = figure(plot_height=400, plot_width=400, title="Raw signal",
              tools="crosshair,pan,reset,save,wheel_zoom")
plot_mfcc.image(image=[data_mfcc], x=[0], y=[0], dw=[10], dh=[10])



file_menu = Select(title="Wybierz plik", value=_BASE_FILE_NAME, options=load_data.get_file_names())



def update_plot_raw_signal():
	new_file_name = file_menu.value
	data = load_data.load_file(new_file_name, _WINDOW_SCALING)
	data_raw_signal.data = dict(x=np.arange(0, _SPARSNESS*len(data), step=_SPARSNESS), y=data)
	# plot_raw_signal.y_range = [min(data), max(data)]
	# plot_raw_signal.x_range = [0, len(data)]

def update_plot_mfcc():
	new_file_name = file_menu.value
	data = load_data.load_raw_file(new_file_name)
	data_mfcc = np.swapaxes(psf.mfcc(data[1], data[0]), 0, 1)
	plot_mfcc.image(image=[data_mfcc], x=[0], y=[0], dw=[10], dh=[10])


def update_data(attrname, old, new):
	update_plot_raw_signal()
	update_plot_mfcc()

file_menu.on_change('value', update_data)


inputs = widgetbox(file_menu)


curdoc().add_root(row(inputs, plot_raw_signal, plot_mfcc, width=1200))
curdoc().title = "Visualization"

