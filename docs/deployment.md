# Production Deployment Guide

## 1. Prerequisites
- Docker & Docker Compose v2+
- Domain name & SSL certificate (Certbot / Let's Encrypt)

## 2. Environment Setup
Copy `.env.example` to `.env` and set production secrets:

```bash
cp .env.example .env
```

Ensure `SECRET_KEY`, `POSTGRES_PASSWORD`, and `CORS_ORIGINS` are securely updated.

## 3. Launching Stack with Docker Compose

```bash
docker compose up -d --build
```

Services will start:
- `api`: `http://localhost:8000`
- `frontend`: `http://localhost:3000`
- `postgres`: `localhost:5432`
- `redis`: `localhost:6379`
- `worker`: Celery worker instance
- `scheduler`: Celery Beat periodic scheduler

## 4. Reverse Proxy Setup (Nginx)

Place an Nginx or Caddy server in front of port 3000 and 8000 with SSL termination.
