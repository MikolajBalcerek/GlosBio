### Uruchomienie projektu

---

#### Używając narzędzia Docker

Potrzebne są:

* **docker** (>=  17.0)
* **docker-compose** (>= 1.23)

---

#### API

* tworzymy kontenery i je odpalamy:

`> docker-compose up -d`

#### Aplikacja webowa

_jeszcze nie skonteneryzowana_


---

#### Ustawiając  środowisko samodzielnie


Potrzebne są:

* Python 3
* pipenv
* npm
* [ffmpeg](http://ffmpeg.org) - dodany do PATH na systemie
* dostęp do bazy MongoDB ze znanym nam adresem oraz portem

#### API

* wchodzimy w folder `Backend`

* przy pierwszym uruchomieniu instalujemy pythonowe zależności
``` > pipenv install  ```

* edytujemy plik `config.py`, należy tu wprowadzić adres oraz port pod którym wystawiona jest baza danych
```
class BaseConfig(object):

	(...)
    # MongoDB database settings
    DATABASE_URL = <adres>
    DATABASE_PORT = <port>
    DATABASE_NAME = "samplebase"
	(...)
```

* uruchamiamy program
```
pipenv run python main.py
```
lub razem z testami
```
pipenv run.py
```

* serwer zostanie domyślnie wystawiony na porcie 5000
 
#### Aplikacja webowa
* wchodzimy w folder `frontend`
* odpalamy `npm install && npm run start`
* okno z apką wyskoczy samo w domyślnej przeglądarce




### Aplikacja mobilna (Android od wersji 4.4)
* wchodzimy do folderu `mobile`
* odpalamy `npm install`
* jeśli nie posiadamy telefonu z Androidem możemu uruchomić aplikację na [emulatorze](https://facebook.github.io/react-native/docs/getting-started)
* jeśli chcemy zainstalować aplikację na telefonie musimy połączyć się z komputerem przez USB i telefon musi być w trybie developerskim
* uruchamiamy aplikację przez `react-native run-android --variant=release` (należy pamętać, że to nie zadziała jeśli mamy już tą aplikację zainstalowaną na telefonie)
