start:
	docker-compose up -d

stop:
	docker-compose stop

remove:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs --follow

logs-api:
	docker-compose logs --follow --tail=30 api

logs-webapp:
	docker-compose logs --follow --tail=30 webapp

logs-db:
	docker-compose logs --follow --tail=30 db

tests-api:
	docker-compose run api python -m unittest
	docker-compose stop
