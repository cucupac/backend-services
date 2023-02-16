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
	coverage report --fail-under=80
