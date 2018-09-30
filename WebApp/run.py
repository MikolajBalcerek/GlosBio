# this just runs the bokeh server, you can also use the command line as well
# bokeh serve --show VisualizationApp

import subprocess

try:
    subprocess.call("bokeh serve --show VisualizationApp")
except FileNotFoundError:
    subprocess.call("pip install pipenv")
    subprocess.call("pipenv install")
    subprocess.call("pipenv run bokeh serve --show VisualizationApp")