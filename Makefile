# Music Sync Hub - Development Makefile
.PHONY: help build up down restart logs clean test lint format install

# Default target
help: ## Show this help message
	@echo "Music Sync Hub - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Development Environment ===
build: ## Build all Docker images
	docker-compose build

up: ## Start all services in development mode
	docker-compose up -d

up-logs: ## Start all services and show logs
	docker-compose up

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

logs-db: ## Show database logs
	docker-compose logs -f postgres

logs-redis: ## Show Redis logs
	docker-compose logs -f redis

# === Production Environment ===
prod-build: ## Build production images
	docker-compose -f docker-compose.prod.yml build

prod-up: ## Start production environment
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## Show production logs
	docker-compose -f docker-compose.prod.yml logs -f

# === Database Operations ===
db-shell: ## Access PostgreSQL shell
	docker-compose exec postgres psql -U music_sync_user -d music_sync_hub

db-backup: ## Create database backup
	docker-compose exec postgres pg_dump -U music_sync_user music_sync_hub > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore: ## Restore database from backup (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "Usage: make db-restore BACKUP_FILE=backup.sql"; exit 1; fi
	docker-compose exec -T postgres psql -U music_sync_user -d music_sync_hub < $(BACKUP_FILE)

# === Redis Operations ===
redis-shell: ## Access Redis CLI
	docker-compose exec redis redis-cli -a music_sync_redis_password

redis-flush: ## Flush all Redis data (WARNING: This will delete all cached data)
	docker-compose exec redis redis-cli -a music_sync_redis_password FLUSHALL

# === Development Tools ===
shell-backend: ## Access backend container shell
	docker-compose exec backend bash

shell-frontend: ## Access frontend container shell
	docker-compose exec frontend sh

# === Testing ===
test: ## Run all tests
	docker-compose exec backend pytest
	docker-compose exec frontend npm test

test-backend: ## Run backend tests
	docker-compose exec backend pytest

test-frontend: ## Run frontend tests
	docker-compose exec frontend npm test

test-coverage: ## Run tests with coverage
	docker-compose exec backend pytest --cov=app --cov-report=html
	docker-compose exec frontend npm run test:coverage

# === Code Quality ===
lint: ## Run linting for all projects
	docker-compose exec backend ruff check .
	docker-compose exec backend black --check .
	docker-compose exec frontend npm run lint

lint-fix: ## Fix linting issues
	docker-compose exec backend ruff check --fix .
	docker-compose exec backend black .
	docker-compose exec frontend npm run lint:fix

format: ## Format code
	docker-compose exec backend black .
	docker-compose exec frontend npm run format

type-check: ## Run type checking
	docker-compose exec backend mypy app
	docker-compose exec frontend npm run type-check

# === Installation ===
install: ## Install dependencies locally (for IDE support)
	@echo "Installing backend dependencies..."
	cd backend && python -m pip install -e ".[dev]"
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing root dependencies..."
	npm install

# === Cleanup ===
clean: ## Remove all containers, images, and volumes
	docker-compose down -v --rmi all --remove-orphans

clean-volumes: ## Remove all volumes (WARNING: This will delete all data)
	docker-compose down -v

prune: ## Remove unused Docker resources
	docker system prune -af

# === Monitoring ===
stats: ## Show container resource usage
	docker stats

ps: ## Show running containers
	docker-compose ps

health: ## Check health of all services
	@echo "=== Service Health Check ==="
	@echo "Backend API:"
	@curl -f http://localhost:8000/health 2>/dev/null && echo " ✓ Healthy" || echo " ✗ Unhealthy"
	@echo "Frontend:"
	@curl -f http://localhost:3000 2>/dev/null && echo " ✓ Healthy" || echo " ✗ Unhealthy"
	@echo "Database:"
	@docker-compose exec postgres pg_isready -U music_sync_user -d music_sync_hub >/dev/null 2>&1 && echo " ✓ Healthy" || echo " ✗ Unhealthy"
	@echo "Redis:"
	@docker-compose exec redis redis-cli -a music_sync_redis_password ping >/dev/null 2>&1 && echo " ✓ Healthy" || echo " ✗ Unhealthy"

# === Quick Setup ===
setup: ## Complete setup for new development environment
	@echo "Setting up Music Sync Hub development environment..."
	cp env.example .env
	@echo "Please edit .env file with your API credentials"
	@echo "Then run: make build && make up"

# === Documentation ===
docs: ## Generate and serve documentation
	@echo "Documentation available in README.md"
	@echo "API docs available at: http://localhost:8000/docs" 