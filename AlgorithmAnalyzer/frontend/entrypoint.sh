#!/bin/bash

npm build
serve -l tcp://0.0.0.0:3000 -s build
