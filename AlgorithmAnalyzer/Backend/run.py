#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this just runs the tests + flask server, you can also use the command line
# python main.py for run
# python -m unittest for tests (run from ./Backend)

import subprocess

try:
    subprocess.call("pipenv run python -m unittest".split(" "))
    subprocess.call("pipenv run python main.py".split(" "))
except FileNotFoundError:
    subprocess.call("pip install pipenv")
    subprocess.call("pipenv install")
    subprocess.call("pipenv run python main.py".split(" "))
