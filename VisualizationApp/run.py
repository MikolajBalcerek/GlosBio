# this just runs the bokeh server, you can also use the command line as well
# bokeh serve --show main.py

import subprocess

try:
    subprocess.call("bokeh serve --show main.py")
except FileNotFoundError:
    subprocess.call("pip install pipenv")
    subprocess.call("pipenv install")
    subprocess.call("pipenv run bokeh serve --show main.py")
    subprocess.call("bokeh serve --show main.py")