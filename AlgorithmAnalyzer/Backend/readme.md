# Algorithm Analyzer Backend REST API
[![Build Status](https://travis-ci.com/MikolajBalcerek/GlosBio.svg?branch=master)](https://travis-ci.com/MikolajBalcerek/GlosBio)
 
[![Coverage Status](https://coveralls.io/repos/github/MikolajBalcerek/GlosBio/badge.svg?branch=master)](https://coveralls.io/github/MikolajBalcerek/GlosBio?branch=master)
![Backend's documentation in browser](https://i.imgur.com/WeSk8Dl.jpg)

### Installing
You have to install [ffmpeg](http://ffmpeg.org) on your system.  
It is available on apt (Linux), brew (MacOS), a binary is available on the website (Windows).
After installing make sure that you added the executables to your PATH.  
Verify by running ffmpeg in the console.

### Running
Use the one-step solution (with tests):
```
python run.py
```

Or using Python 3:
```
pip install pipenv
pipenv install
pipenv run python main.py
```

You can browse the API in browser at http://127.0.0.1:5000/

After the slash enter the endpoint's name

### Tests
#### Running tests
From ./Backend run:
```
pipenv run python -m unittest
```

#### Test coverage
For checking test coverage using coverage.py library:
```
pipenv run coverage run -m unittest
```
For results either type: ```pipenv run coverage report``` (in console)
or  ```pipenv run coverage html``` to create html directory with logs.

![Tests coverage in HTML form](https://i.imgur.com/mMnOGv1.jpg)