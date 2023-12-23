## Configuration
## =============

# Have zero effect by default to prevent accidental changes.
.DEFAULT_GOAL := help

# Delete targets that fail to prevent subsequent attempts incorrectly assuming
# the target is up to date.
.DELETE_ON_ERROR: ;

# Prevent pesky default rules from creating unexpected dependency graphs.
.SUFFIXES: ;


## Verbs
## =====

## Print this help message
help:
	@./bin/mkhelp.py help < $(MAKEFILE_LIST)
.PHONY: help

## Install the recommended dependencies for development
sync_env:
	poetry install --sync

## Checks
## ------

## Run all checks
check_all: check_format check_lint check_tests check_types;
.PHONY: check

## Run formatters for all parts of the project
check_format:
	isort --check .
	black --check .
.PHONY: check_format

## Run linters for all parts of the project
check_lint:
	ruff bin/
.PHONY: check_lint

## Run unit tests for all parts of the project
check_tests:
	pytest \
		--durations=10 \
		--doctest-modules src/env_logger \
		tests/
.PHONY: check_tests


## Run type checkers for python code
check_types:
	mypy --package env_logger
.PHONY: check_types

## Fixes
## -----

## Attempt to fix formatting problems
fix_format:
	isort .
	black .
.PHONY: fix_format

## Attempt to fix linting problems
fix_lint:
	ruff --fix
.PHONY: fix_lint


## Nouns
## =====

./bin/mkhelp.py:
	mkhelp print_script > $@
	chmod +x $@

constraints.txt: poetry.lock
	poetry export \
		--format=constraints.txt \
		--output=$@ \
		--with dev \
		--without-hashes
