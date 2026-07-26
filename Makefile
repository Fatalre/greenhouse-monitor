SHELL := /bin/bash
.PHONY: dev prod down logs test lint build migrate admin seed backup restore

dev:
	docker compose up --build

prod:
	docker compose -f docker-compose.production.yml up -d --build

down:
	docker compose -f docker-compose.production.yml down

logs:
	docker compose -f docker-compose.production.yml logs -f --tail=200

migrate:
	docker compose -f docker-compose.production.yml run --rm backend alembic upgrade head

admin:
	docker compose -f docker-compose.production.yml run --rm backend python -m app.cli create-admin

seed:
	docker compose run --rm backend python -m app.cli seed

test:
	cd apps/backend && pytest -q
	cd apps/frontend && npm test -- --run

lint:
	cd apps/backend && ruff check app tests && mypy app
	cd apps/frontend && npm run lint && npm run typecheck

build:
	cd apps/frontend && npm run build

backup:
	./deploy/scripts/backup.sh

restore:
	./deploy/scripts/restore.sh $(FILE)
