start:
	docker-compose up -d

stop:
	docker-compose stop

remove:
	docker-compose down

build-images: build-image-api build-image-webapp

build-image-api:
	docker-compose build api

build-image-webapp:
	docker-compose build webapp

build-webapp:
	docker-compose run webapp /opt/node_modules/.bin/react-scripts build

logs:
	docker-compose logs --follow

logs-api:
	docker-compose logs --follow --tail=30 api

logs-webapp:
	docker-compose logs --follow --tail=30 webapp

logs-db:
	docker-compose logs --follow --tail=30 db

tests-api:
	docker-compose run --rm api python -m unittest
	docker-compose stop db

populate-api-tags:
	docker-compose run api python populate_tags.py


