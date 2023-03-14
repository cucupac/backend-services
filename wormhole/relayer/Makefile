SHELL := /bin/bash

docker_image = wormhole-relayer
docker_username = axprotocol
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
	@echo Checking relayer format...
	isort $(formatted_code) --check
	black --check $(formatted_code)

lint:
	@echo Linting relayer...
	pylint $(formatted_code) --fail-under=9.5

run:
	python -m app --reload

make run-container:
	docker-compose up -d

build:
	docker build -t $(docker_username)/$(docker_image):latest .

push:
	docker push $(docker_username)/$(docker_image):latest

test:
	@echo Running relayer unit tests...
	coverage run --source app -m pytest tests --color=yes
	coverage report --fail-under=80