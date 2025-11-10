# Makefile to bootstrap the project with Poetry and run tests
# Usage:
#   make bootstrap    # install poetry (if needed), configure venv and install deps
#   make install-poetry
#   make configure-venv
#   make install      # install dependencies (no-root)
#   make test         # run pytest under poetry
#   make run          # run the main script via poetry
#   make shell        # spawn a poetry shell

.PHONY: help bootstrap install-poetry configure-venv install test run shell clean

help:
	@echo "Makefile targets:"
	@echo "  bootstrap       Install Poetry (if missing), configure in-project venv, and install deps"
	@echo "  install-poetry  Install Poetry using the official installer (if not already present)"
	@echo "  configure-venv  Configure Poetry to create virtualenvs in .venv (in-project)"
	@echo "  install         Install project dependencies (uses --no-root to skip packaging the project)"
	@echo "  test            Run pytest inside Poetry environment"
	@echo "  run             Run the main script via Poetry"
	@echo "  shell           Activate Poetry shell (interactive)"
	@echo "  clean           Remove .venv and recorded VCR cassettes (optional)"

install-poetry:
	@command -v poetry >/dev/null 2>&1 || ( \
		echo "Poetry not found — installing via official installer..."; \
		curl -sSL https://install.python-poetry.org | python3 - && \
		echo "Poetry installed. You may need to add \"$HOME/.local/bin\" to your PATH." \
	)
	@command -v poetry >/dev/null 2>&1 && echo "Poetry is available: $$(poetry --version)" || true

configure-venv:
	@poetry config virtualenvs.in-project true --local
	@echo "Configured Poetry to create .venv in project root"

install: configure-venv
	@poetry install --no-root

bootstrap: install-poetry install
	@echo "Bootstrap complete. To run tests: make test"

test:
	@poetry run pytest -q

run:
	@poetry run python main.py

shell:
	@poetry shell

clean:
	@rm -rf .venv
	@echo "Removed .venv"
	@find tests/fixtures/cassettes -name "*.yaml" -delete || true
	@echo "Removed recorded cassettes"

