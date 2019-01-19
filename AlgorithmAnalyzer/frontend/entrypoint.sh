#!/bin/bash

# npm run build
/opt/node_modules/.bin/react-scripts build
serve -l tcp://0.0.0.0:3000 -s build
