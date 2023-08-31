SHELL := /bin/bash

docker_image = gas-system
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
	@echo Checking gas_system format...
	isort $(formatted_code) --check
	black --check $(formatted_code)

lint:
	@echo Linting gas_system...
	pylint $(formatted_code) --fail-under=9.5

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
	@echo Running gas_system unit tests...
	coverage run --source app -m pytest tests --color=yes
	coverage report --fail-under=68

migration:
	@if [ -z $(rev_id)] || [ -z $(migration_message)]; \
	then \
		echo -e "\n\nERROR: make migration requires both a rev_id and a migration_message.\nEXAMPLE: make migration rev_id=0001 migration_message=\"my message\"\n\n"; \
	else \
		alembic revision --autogenerate --rev-id "$(rev_id)" -m "$(migration_message)"; \
	fi

migration-sql:
	alembic upgrade head --sql

migrate:
	alembic upgrade head