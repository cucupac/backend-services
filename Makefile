SHELL := /bin/bash

rev_id = ""
migration_message = ""

.ONESHELL:

.PHONY: test run

requirements.txt: requirements.in
	pip-compile --quiet --generate-hashes --allow-unsafe --resolver=backtracking --output-file=$@

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