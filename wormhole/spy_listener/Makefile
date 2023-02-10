SHELL := /bin/bash

docker_image = spy_listener
docker_username = ax_protocol
formatted_code := app/ tests/
rev_id = ""
migration_message = ""

.ONESHELL:

.PHONY: test run

requirements.txt: requirements.in
	pip-compile --quiet --generate-hashes --allow-unsafe --resolver=backtracking --output-file=$@

format:
	isort $(formatted_code)
	black $(formatted_code)

format-check:
	@echo Checking spy_listener format...
	isort $(formatted_code) --check
	black --check $(formatted_code)

lint:
	@echo Linting spy_listener...
	pylint --ignore-paths=app/infrastructure/clients/streams/grpc $(formatted_code)

run:
	python -m app --reload

make run-container:
	docker-compose up -d

build:
	docker build -t $(docker_username)/$(docker_image):latest .

push:
	docker push $(docker_username)/$(docker_image):latest

test:
	@echo Running spy_listener unit tests...
	coverage run --source app -m pytest tests --color=yes
	coverage report --fail-under=50

# Call more than one service
# test: build
# 	function removeContainers {
# 		docker-compose -p spy_listener_ci rm -s -f test_db
# 	}
# 	trap removeContainers EXIT
# 	docker-compose -p spy_listener_ci run --rm ci


migration:
	if [ -z $(rev_id)] || [ -z $(migration_message)]; \
	then \
		echo -e "\n\nmake migration requires both a rev_id and a migration_message.\nExample usage: make migration rev_id=0001 migration_message=\"my message\"\n\n"; \
	else \
		alembic revision --autogenerate --rev-id "$(rev_id)" -m "$(migration_message)"; \
	fi

migrate:
	alembic upgrade head

# test comment 6