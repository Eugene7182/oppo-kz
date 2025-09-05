# Quick commands
.PHONY: help dev-up dev-down migrate smoke
help:
	@echo "make dev-up    - run docker-compose (db+backend+frontend)"
	@echo "make dev-down  - stop compose"
	@echo "make migrate   - alembic upgrade head"
	@echo "make smoke     - run e2e smoke script"
dev-up:
	docker-compose up -d
dev-down:
	docker-compose down -v
migrate:
	./infra/scripts/migrate.sh
smoke:
	BASE_URL?=http://localhost:8000; ADMIN_USER?=admin@oppo.kz; ADMIN_PASS?=StrongPass123; \
	bash -lc "BASE_URL=$$BASE_URL ADMIN_USER=$$ADMIN_USER ADMIN_PASS=$$ADMIN_PASS ./infra/scripts/smoke.sh"


wipe:
	CONFIRM?=NO; DRY_RUN?=true; \
	bash -lc "CONFIRM=$$CONFIRM DRY_RUN=$$DRY_RUN ./infra/scripts/wipe_demo.sh"

seed-full:
	bash -lc "./infra/scripts/seed_full.sh"

load-sales:
	DAYS?=30; PER_DAY?=50; STORES?=A01,A02; SKUS?=OPPO-A1K,OPPO-RENO10,OPPO-ENCOBUDS2; PROMOTER?=pavlov; \
	bash -lc "DAYS=$$DAYS PER_DAY=$$PER_DAY STORES=$$STORES SKUS=$$SKUS PROMOTER=$$PROMOTER ./infra/scripts/seed_sales_bulk.sh"
