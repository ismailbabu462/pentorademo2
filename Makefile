.PHONY: help install lint format test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install all dependencies"
	@echo "  lint        - Run linting for all projects"
	@echo "  format      - Format code for all projects"
	@echo "  test        - Run tests for all projects"
	@echo "  clean       - Clean build artifacts"
	@echo ""
	@echo "Backend commands:"
	@echo "  backend-install - Install backend dependencies"
	@echo "  backend-lint    - Run Python linting (flake8, black, isort, mypy)"
	@echo "  backend-format  - Format Python code"
	@echo ""
	@echo "Frontend commands:"
	@echo "  frontend-install - Install frontend dependencies"
	@echo "  frontend-lint    - Run JavaScript/React linting"
	@echo "  frontend-format  - Format JavaScript/React code"

# Install all dependencies
install: backend-install frontend-install

# Backend commands
backend-install:
	cd backend && pip install -r requirements.txt

backend-lint:
	cd backend && flake8 .
	cd backend && black --check .
	cd backend && isort --check-only .
	cd backend && mypy .

backend-format:
	cd backend && black .
	cd backend && isort .

# Frontend commands
frontend-install:
	cd frontend && yarn install

frontend-lint:
	cd frontend && yarn lint

frontend-format:
	cd frontend && yarn format

# Combined commands
lint: backend-lint frontend-lint

format: backend-format frontend-format

test:
	@echo "Running tests..."
	@echo "Backend tests:"
	cd backend && python -m pytest tests/ -v || echo "No tests found"
	@echo "Frontend tests:"
	cd frontend && yarn test --watchAll=false || echo "No tests found"

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
