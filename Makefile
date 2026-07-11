override SHELL := /bin/bash

COMPOSE_PROD := docker compose -f docker-compose.prod.yml

.PHONY: all
all: clean dev

.PHONY: setup
setup:
	@if [ -f backend/.db.env ]; then \
		echo 'backend/.db.env already exists, leaving it untouched.'; \
	else \
		echo 'Creating backend/.db.env with a generated database password...'; \
		sed "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$$(openssl rand -base64 32)|" \
			backend/.db.env.template > backend/.db.env; \
		echo 'Done. Run "make dev" to start CipherMoth.'; \
	fi

# Development: local, build from source, hot-reload (UI :3000, API :8000)

.PHONY: dev
dev:
	@echo 'Starting the dev stack with hot-reload (UI :3000, API :8000)...'
	docker compose up -d --build

.PHONY: down
down:
	@echo 'Stopping the dev stack (database volume is kept)...'
	docker compose down

.PHONY: clean
clean:
	@echo 'Removing the dev stack and its database volume...'
	-docker compose down --volumes --remove-orphans --rmi local
	@echo 'Removing cache files...'
	-find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

# Production: the real vault, run from prebuilt GHCR images (needs a sibling .env)

.PHONY: prod-up
prod-up:
	@echo 'Pulling and starting the production stack from GHCR images...'
	$(COMPOSE_PROD) up -d

.PHONY: prod-down
prod-down:
	@echo 'Stopping the production stack (database volume is kept)...'
	$(COMPOSE_PROD) down

.PHONY: clean-prod
clean-prod:
	@echo 'WARNING: this DESTROYS the production database volume -> your real vault.'
	@echo 'There is no password recovery. This cannot be undone.'
	@read -r -p 'Type "destroy" to confirm: ' ans; \
	if [ "$$ans" = "destroy" ]; then \
		$(COMPOSE_PROD) down --volumes --remove-orphans; \
		echo 'Production stack and volume removed.'; \
	else \
		echo 'Aborted. Nothing was removed.'; \
	fi

.PHONY: lint
lint:
	cd backend && uv run ruff check .
	cd frontend && npm run lint

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
	cd frontend && npm run lint && npm run format:check
