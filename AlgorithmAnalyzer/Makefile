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
	docker-compose logs api --follow --tail=30

logs-webapp:
	docker-compose logs webapp --follow --tail=30

logs-db:
	docker-compose logs webapp --follow --tail=30

tests-api:
	docker-compose run api python -m unittest
	docker-compose stop
