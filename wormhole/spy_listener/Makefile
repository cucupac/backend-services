SHELL := /bin/bash

docker_image = wormhole-spy-listener
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
	@echo Checking spy_listener format...
	isort $(formatted_code) --check
	black --check $(formatted_code)

lint:
	@echo Linting spy_listener...
	pylint --ignore-paths=app/infrastructure/clients/streams/grpc $(formatted_code) --fail-under=9.5

run:
	python -m app --reload

check-dockerignore:
	@if [ ! -f .dockerignore ]; then \
		echo "Error: .dockerignore file not found. Please add a .dockerignore file before proceeding."; \
		exit 1; \
	fi
	@if ! grep -q '^[[:space:]]*\.env' .dockerignore; then \
		echo "Error: .env was not found in .dockerignore. Please add it before proceeding."; \
		exit 1; \
	fi

run-container: check-dockerignore
	docker-compose up -d

build: check-dockerignore
	docker build -t $(docker_username)/$(docker_image):latest .

push: check-dockerignore
	docker push $(docker_username)/$(docker_image):latest

test:
	@echo Running spy_listener unit tests...
	coverage run --source app -m pytest tests --color=yes
	coverage report --fail-under=75