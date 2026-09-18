.PHONY: help dev build test lint up down clean

help:
	@echo "Available commands:"
	@echo "  make up          - Start all services with Docker Compose"
	@echo "  make down        - Stop all Docker Compose services"
	@echo "  make dev-backend - Run backend API locally with uvicorn"
	@echo "  make dev-frontend- Run frontend locally with Vite"
	@echo "  make test        - Run backend test suite"
	@echo "  make build       - Build production container images"
	@echo "  make clean       - Remove cache and build artifacts"

up:
	docker compose up --build

down:
	docker compose down

dev-backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest tests/ -v

build:
	docker compose build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf frontend/dist
