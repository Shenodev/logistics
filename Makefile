.PHONY: setup migrate seed demo clean-db help

PY ?= backend/.venv/Scripts/python.exe
ifeq (,$(wildcard $(PY)))
  PY = backend/.venv/bin/python
endif
ifeq (,$(wildcard $(PY)))
  PY = python
endif

help: ## Show targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: migrate seed ## One-click: migrate + seed_demo (same as ./setup.sh)

migrate: ## Run Django migrations (sqlite fallback if no DATABASE_URL)
	@$(PY) backend/manage.py migrate --noinput

seed: ## Seed demo accounts + Faker data (57 orders, 24 invoices, alerts)
	@$(PY) backend/manage.py seed_demo --clear

demo: setup ## Alias for setup

clean-db: ## Delete sqlite DB (only when using sqlite)
	@rm -f backend/db.sqlite3
	@echo "Removed backend/db.sqlite3"
