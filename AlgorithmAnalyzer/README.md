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
* okno z aplikacją wyskoczy samo w domyślnej przeglądarce
