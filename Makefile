override SHELL := /bin/bash

.PHONY: all
all: clean buildup

.PHONY: clean
clean:
	@echo 'Removing containers...'
	-docker compose down --volumes --remove-orphans --rmi local
	@echo 'Removing cache files...'
	-find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

.PHONY: buildup
buildup:
	@echo 'Building and starting containers...'
	docker compose up -d --build
