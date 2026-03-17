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

.PHONY: dev
dev:
	@echo 'Starting in development mode (hot-reload)...'
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

.PHONY: lint
lint:
	cd backend && uv run ruff check .

.PHONY: typecheck
typecheck:
	cd backend && uv run ty check .

.PHONY: format
format:
	cd backend && uv run ruff format .
	cd frontend && npm run format

.PHONY: check
check:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run ty check .
	cd frontend && npm run format:check
