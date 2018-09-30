from math import ceil
from os.path import dirname, join

import numpy as np
import python_speech_features as psf
from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, Slider, Div
from bokeh.models.widgets import Slider, TextInput, Select
from bokeh.plotting import figure
from bokeh.palettes import YlGn3

import audio
from audio import MAX_FREQ, TIMESLICE, NUM_BINS
from waterfall import WaterfallRenderer

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

MAX_FREQ_KHZ = MAX_FREQ*0.001
NUM_GRAMS = 800
GRAM_LENGTH = 512
TILE_WIDTH = 200
EQ_CLAMP = 20

PALETTE = ['#081d58', '#253494', '#225ea8', '#1d91c0', '#41b6c4', '#7fcdbb', '#c7e9b4', '#edf8b1', '#ffffd9']
PLOTARGS = dict(tools="", toolbar_location=None, outline_line_color='#595959')

filename = join(dirname(__file__), "description.html")
desc = Div(text=open(filename).read(),
           render_as_text=False, width=1000)

waterfall_renderer = WaterfallRenderer(palette=PALETTE, num_grams=NUM_GRAMS,
                                       gram_length=GRAM_LENGTH, tile_width=TILE_WIDTH)
waterfall_plot = figure(plot_width=990, plot_height=300, min_border_left=80,
                        x_range=[0, NUM_GRAMS], y_range=[0, MAX_FREQ_KHZ], **PLOTARGS)
waterfall_plot.grid.grid_line_color = None
waterfall_plot.background_fill_color = "#024768"
waterfall_plot.renderers.append(waterfall_renderer)

signal_source = ColumnDataSource(data=dict(t=[], y=[]))
signal_plot = figure(plot_width=600, plot_height=200, title="Signal",
                     x_range=[0, TIMESLICE], y_range=[-0.8, 0.8], **PLOTARGS)
signal_plot.background_fill_color = "#eaeaea"
signal_plot.line(x="t", y="y", line_color="#024768", source=signal_source)

spectrum_source = ColumnDataSource(data=dict(f=[], y=[]))
spectrum_plot = figure(plot_width=600, plot_height=200, title="Power Spectrum",
                       y_range=[10**(-4), 10**3], x_range=[0, MAX_FREQ_KHZ],
                       y_axis_type="log", **PLOTARGS)
spectrum_plot.background_fill_color = "#eaeaea"
spectrum_plot.line(x="f", y="y", line_color="#024768", source=spectrum_source)

eq_angle = 2*np.pi/NUM_BINS
eq_range = np.arange(EQ_CLAMP, dtype=np.float64)
eq_data = dict(
    inner=np.tile(eq_range+2, NUM_BINS),
    outer=np.tile(eq_range+2.95, NUM_BINS),
    start=np.hstack([np.ones_like(eq_range)*eq_angle*(i+0.05) for i in range(NUM_BINS)]),
    end=np.hstack([np.ones_like(eq_range)*eq_angle*(i+0.95) for i in range(NUM_BINS)]),
    alpha=np.tile(np.zeros_like(eq_range), NUM_BINS),
)
eq_source = ColumnDataSource(data=eq_data)
eq = figure(plot_width=400, plot_height=400,
            x_axis_type=None, y_axis_type=None,
            x_range=[-20, 20], y_range=[-20, 20], **PLOTARGS)
eq.background_fill_color = "#eaeaea"
eq.annular_wedge(x=0, y=0, fill_color="#024768", fill_alpha="alpha", line_color=None,
                 inner_radius="inner", outer_radius="outer", start_angle="start", end_angle="end",
                 source=eq_source)

freq = Slider(start=1, end=MAX_FREQ, value=MAX_FREQ, step=1, title="Frequency")

gain = Slider(start=1, end=20, value=1, step=1, title="Gain")

def update():
    signal, spectrum, bins = audio.data['values']

    # seems to be a problem with Array property, using List for now
    waterfall_renderer.latest = spectrum.tolist()
    waterfall_plot.y_range.end = freq.value*0.001

    # the if-elses below are small optimization: avoid computing and sending
    # all the x-values, if the length has not changed

    if len(signal) == len(signal_source.data['y']):
        signal_source.data['y'] = signal*gain.value
    else:
        t = np.linspace(0, TIMESLICE, len(signal))
        signal_source.data = dict(t=t, y=signal*gain.value)

    if len(spectrum) == len(spectrum_source.data['y']):
        spectrum_source.data['y'] = spectrum
    else:
        f = np.linspace(0, MAX_FREQ_KHZ, len(spectrum))
        spectrum_source.data = dict(f=f, y=spectrum)
    spectrum_plot.x_range.end = freq.value*0.001

    alphas = []
    for x in bins:
        a = np.zeros_like(eq_range)
        N = int(ceil(x))
        a[:N] = (1 - eq_range[:N]*0.05)
        alphas.append(a)
    eq_source.data['alpha'] = np.hstack(alphas)
curdoc().add_periodic_callback(update, 80)

controls = row(widgetbox(gain), widgetbox(freq))

plots = column(waterfall_plot, row(column(signal_plot, spectrum_plot), eq))

curdoc().add_root(desc)
curdoc().add_root(controls)
curdoc().add_root(plots)


