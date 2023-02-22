SHELL := /bin/bash

docker_image = gas_system
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
	@echo Checking gas_system format...
	isort $(formatted_code) --check
	black --check $(formatted_code)

lint:
	@echo Linting gas_system...
	pylint $(formatted_code) --fail-under=9.5

run:
	python -m app --reload

make run-container:
	docker-compose up -d

build:
	docker build -t $(docker_username)/$(docker_image):latest .

push:
	docker push $(docker_username)/$(docker_image):latest

# TODO: Change to --fail-under=80
test:
	@echo Running gas_system unit tests...
	coverage run --source app -m pytest tests --color=yes
	coverage report --fail-under=60