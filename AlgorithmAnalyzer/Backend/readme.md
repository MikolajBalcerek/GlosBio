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
