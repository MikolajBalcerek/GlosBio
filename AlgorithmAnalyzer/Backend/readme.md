# Algorithm Analyzer backend


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

### Tests only
From ./Backend run:
```
pipenv run python -m unittest
```

### Info

#### JSON
A JSON file is stored for each of the recordings.
```
{"name": "Unnormalised Name", "recognized_speech": "Some text"}
```

#### Algorithms
### To add an algorithms to the aplication one must
 - create a class derivina after the class Algorithm, which is here [base_algorithm.py](algorithms/base_algorithm.py)
 - the class should implement abstract methods of Algorithm to provide communication
   between itself and the application
 - import the class and add it to the `ALG_DICT` in [__init__.py](algorithms/algorithms/__init__.py)
 - both binary and multilabel algorithms are supported, for more information read the docstrings in [base_algorithm.py](algorithms/base_algorithm.py)