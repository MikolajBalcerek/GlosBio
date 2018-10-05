#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this just runs the flask server, you can also use the command line as well
# python main.py

import subprocess

try:
    subprocess.call("pipenv run python main.py".split(" "))
except FileNotFoundError:
    subprocess.call("pip install pipenv")
    subprocess.call("pipenv install")
    subprocess.call("pipenv run python main.py".split(" "))
