.PHONY: dev dev-build dev-down dev-logs test lint format clean setup

# ─── Development ───────────────────────────────────────────
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v

dev-logs:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# ─── Testing ───────────────────────────────────────────────
test-backend:
	docker compose exec api pytest --cov=app --cov-report=term-missing

test-frontend:
	docker compose exec frontend npm run test

test-e2e:
	npx playwright test

# ─── Linting & Formatting ─────────────────────────────────
lint:
	ruff check backend/
	mypy backend/
	cd frontend && npm run lint && npm run typecheck

format:
	ruff format backend/
	cd frontend && npm run format

# ─── Database ──────────────────────────────────────────────
migrate:
	docker compose exec api alembic upgrade head

migrate-downgrade:
	docker compose exec api alembic downgrade -1

revision:
	docker compose exec api alembic revision --autogenerate -m "$(message)"

seed:
	docker compose exec api python scripts/seed_db.py

# ─── Production ────────────────────────────────────────────
prod:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

# ─── Utilities ─────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache coverage htmlcov

setup:
	cp .env.example .env
	cd frontend && npm install
	cd backend && poetry install
	docker compose up -d postgres redis
	sleep 3
	docker compose exec api alembic upgrade head
	docker compose exec api python scripts/seed_db.py
	@echo "✓ Setup complete! Run 'make dev' to start."

help:
	@echo "Available commands:"
	@echo "  make dev            Start development environment"
	@echo "  make dev-build      Rebuild and start"
	@echo "  make dev-down       Stop and remove volumes"
	@echo "  make test-backend   Run backend tests"
	@echo "  make test-frontend  Run frontend tests"
	@echo "  make lint           Run linters"
	@echo "  make format         Run formatters"
	@echo "  make migrate        Run database migrations"
	@echo "  make seed           Seed sample data"
	@echo "  make setup          Initial project setup"
