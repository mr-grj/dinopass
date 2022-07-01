override SHELL := /bin/bash

COMPOSE=docker-compose -f docker-compose.yml

.PHONY: all
all: clean buildup shell

.PHONY: clean
clean:
	@echo 'Removing container ...'
	-docker-compose down --volumes --remove-orphans --rmi local
	@echo 'Container removed.'

	@echo 'Removing cache files ...'
	-find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	@echo 'Cache files removed.'

.PHONY: buildup
buildup:
	@echo 'Building container ...'
	${COMPOSE} up -d --build

.PHONY: shell
shell:
	${COMPOSE} exec cli bash

require-%-arg:
	@if [ -z ${${*}} ]; then \
	  echo "ERROR: [$*] argument is required, e.g. $*=<value>"; \
	  exit 1; \
	fi

require-%-tool:
	@if [ "$(shell command -v ${*} 2> /dev/null)" = "" ]; then \
	  echo "ERROR: [$*] not found"; \
	  exit 1; \
	fi
