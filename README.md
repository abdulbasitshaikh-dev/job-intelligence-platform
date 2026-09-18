# Job Intelligence Platform 🚀

[![CI/CD Pipeline](https://github.com/job-intelligence-platform/workflows/ci.yml/badge.svg)](https://github.com/job-intelligence-platform)
[![Python Version](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React / Next](https://img.shields.io/badge/React-18+-cyan.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)

A production-grade, automated **Job Intelligence Platform** built with a modular monolith architecture. Designed to automatically discover, ingest, normalize, deduplicate, score match, filter, track, and deliver job opportunities from public sources.

---

## 🌟 Key Features

- 🔒 **Security & Authentication**: Argon2id password hashing, JWT Access + Refresh token architecture, role-based authorization boundaries (User vs Superuser Admin).
- 🕷️ **Extensible Scraping Engine**: Modular `BaseScraper` supporting HTTP (`httpx` + `BeautifulSoup4` + `lxml`), structured JSON APIs (`RemoteOK`), and browser automation (`Playwright`).
- 🧹 **Normalization & Multi-Tier Deduplication**: Converts messy scraped data into a clean canonical schema. Prevents duplicate jobs using SHA256 hashes of `normalized(title) + normalized(company) + normalized(location)`, canonical URLs, and `(source_id, external_id)`.
- 🎯 **Deterministic Matching Engine**: Computes explainable match scores (0–100%) against user preferences (keywords, location, remote/hybrid, employment type, salary) with granular score breakdowns.
- 📌 **Saved Jobs & Application Tracking**: Bookmark jobs and track application lifecycle statuses (*Interested, Applied, Interviewing, Offer Received, Rejected, Withdrawn*) with editable logs & notes.
- ⚡ **Background Tasks & Scheduling**: Celery + Redis task queue with Celery Beat scheduler for automated, isolated background scraping and notification dispatching.
- 🔔 **Event-Driven Notifications & Webhooks**: Integrates with external tools like **n8n**, Slack, Telegram, or email notifications via standard JSON webhooks.
- 📊 **Administrative Dashboard & Telemetry**: Full administrative visibility into scraper runs, health, consecutive failures, manual trigger controls, and telemetry statistics.
- 🎨 **Modern Responsive Frontend**: Dark mode glassmorphic dashboard built with React, TypeScript, and Tailwind CSS.

---

## 🏗️ Architecture

```
                  DATA SOURCES
                       |
          +------------+------------+
          |            |            |
       HTTP/API     HTML        Browser
          |         Scraper      Automation
          |            |            |
          +------------+------------+
                       |
                       v
                 INGESTION LAYER
                       |
                       v
                NORMALIZATION
                       |
                       v
                VALIDATION & DEDUPLICATION
                       |
                       v
                  PostgreSQL 16
                       |
          +------------+------------+
          |            |            |
          v            v            v
       Search       Matching     Analytics
          |            |
          +------------+
                       |
                       v
                 Notifications & Webhooks (n8n)
```

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.12+, FastAPI, Pydantic v2
- **Database & Migrations**: SQLAlchemy 2.x (asyncpg), PostgreSQL 16, Alembic
- **Background Processing & Queues**: Celery, Redis 7, Celery Beat
- **Scraping & Automation**: `httpx`, `BeautifulSoup4`, `lxml`, `Playwright` Chromium
- **Frontend Stack**: React / Next.js, TypeScript, Tailwind CSS, Lucide Icons, Vite
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Testing & Quality**: pytest, pytest-asyncio, Ruff

---

## 🚀 Quick Start (Docker Compose)

The entire application stack (API, PostgreSQL, Redis, Worker, Scheduler, Frontend) can be launched with Docker Compose:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/job-intelligence-platform.git
cd job-intelligence-platform

# 2. Copy environment configuration
cp .env.example .env

# 3. Launch container stack
docker compose up --build
```

Access the services:
- 🌐 **Frontend Dashboard**: `http://localhost:3000`
- ⚙️ **FastAPI OpenAPI Swagger**: `http://localhost:8000/docs`
- 🏥 **Health Check**: `http://localhost:8000/health/ready`

---

## 🧪 Running Automated Tests

Run the backend test suite (Unit tests for normalization, matching engine, security, integration tests, and scraper mocks):

```bash
cd backend
pytest tests/ -v
```

---

## 📖 Documentation Directory

Detailed operations & architecture guides are located in `/docs`:

- 📐 [Architecture Overview](docs/architecture.md)
- 🕷️ [Scraper Development Guide](docs/scraper-development.md)
- 🔌 [REST API Reference](docs/api.md)
- 🚀 [Deployment Guide](docs/deployment.md)
- 📊 [Operations & Observability](docs/operations.md)
- 🔗 [n8n Integration Guide](docs/n8n-integration.md)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
