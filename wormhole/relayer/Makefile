SHELL := /bin/bash

docker_image = relayer
docker_username = ax_protocol
formatted_code := app/ tests/ tasks.py
rev_id = ""
migration_message = ""

.ONESHELL:

.PHONY: test run

requirements.txt: requirements.in
	pip-compile --quiet --generate-hashes --allow-unsafe --resolver=backtracking --output-file=$@

format:
	isort $(formatted_code)
	black $(formatted_code)

lint:
	pylint app

run:
	python -m app --reload

make run-container:
	docker-compose up -d

build:
	docker build -t $(docker_username)/$(docker_image):latest .

push:
	docker push $(docker_username)/$(docker_image):latest

# Call more than one service
test: build
	function removeContainers {
		docker-compose -p relayer_ci rm -s -f test_db
	}
	trap removeContainers EXIT
	docker-compose -p relayer_ci run --rm ci