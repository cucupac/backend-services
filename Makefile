SHELL := /bin/bash

.ONESHELL:

.PHONY: test run


make run-container:
	docker-compose up -d


# TODO: Call more than one service
test: build
	function removeContainers {
		docker-compose -p spy_listener_ci rm -s -f test_db
	}
	trap removeContainers EXIT
	docker-compose -p spy_listener_ci run --rm ci