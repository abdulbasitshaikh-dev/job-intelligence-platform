# Job Intelligence Platform 🚀

[![CI/CD Pipeline](https://github.com/job-intelligence-platform/workflows/ci.yml/badge.svg)](https://github.com/job-intelligence-platform)
[![Python Version](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-cyan.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5+-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5+-purple.svg)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)

A production-grade, automated **Job Intelligence Platform** built with a modular monolith architecture. Designed to automatically discover, ingest, normalize, deduplicate, score match, filter, track, and deliver job opportunities from legal, public sources.

---

## 🌟 Architecture & Capabilities

### ✅ Implemented Core Systems
- 🔒 **Security & Authentication**: Argon2id password hashing, JWT Access + Refresh token architecture, role-based boundaries (Visitor vs Authenticated User vs Superuser Admin).
- 🕷️ **Legal & Observable Scraping**: Modular `BaseScraper` with structured HTTP adapters (`RemoteOK`, `Arbeitnow`), per-item error isolation, failure counters, and exponential backoff.
- 🧹 **Canonical Normalization & Deduplication**: Cleans HTML entities, deduplicates geographic location parts (e.g. `California, California, US` &rarr; `California, US`), repairs inverted salary bounds, and generates a SHA-256 fingerprint from `(source_id, normalized_title, normalized_company, normalized_location)`.
- 🎯 **Two-Tier Search & Matching Engine**:
  - **Search Relevance**: SQL-level weighted relevance ranking matching Title prefix/substring before Company/Location/Description.
  - **Personalized Match Score**: Multi-attribute evaluation across 5 dimensions (Keywords, Location, Work Mode, Employment Type, Salary) with a 0–100 score and explainable point breakdown.
- 📌 **Application Tracking & Bookmarks**: Real-time state persistence for saved opportunities and Kanban application lifecycle tracking (*Interested, Applied, Interviewing, Offer Received, Rejected, Withdrawn*).
- ⚡ **Background Queues & Stale Job Lifecycle**: Celery + Redis task queue with Celery Beat scheduler. Automated 30-day stale job deactivation and automatic reactivation when active postings reappear.
- 🛡️ **SSRF-Hardened Webhook Notifications**: Real-time webhook dispatching protected against private IP / loopback / cloud metadata addresses, complete with HMAC-SHA256 request signatures (`X-JobIntel-Signature`) and deduplicated delivery logs (`NotificationLog`).
- 📊 **Administrative Telemetry & Health Monitoring**: Live status dashboard displaying PostgreSQL, Redis, and Celery Scheduler health, run metrics, manual scrape triggers, and global source sync.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.x (asyncpg & psycopg2)
- **Database**: PostgreSQL 16, Alembic database migrations
- **Distributed Queues**: Celery, Redis 7, Celery Beat
- **Scraping & Automation**: `httpx`, `BeautifulSoup4`, `lxml`, `Playwright` Chromium
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **DevOps**: Docker, Docker Compose (`docker-compose.yml`, `docker-compose.prod.yml`), GitHub Actions

---

## 🚀 Quick Start (Docker Compose)

### 1. Development Mode
```bash
# Clone the repository
git clone https://github.com/your-username/job-intelligence-platform.git
cd job-intelligence-platform

# Copy environment variables
cp .env.example .env

# Start all containers in development mode (with code reload)
docker compose up --build
```

### 2. Production Mode
```bash
# Run production compose (no dev bind mounts, multi-worker uvicorn, strict restart policies)
docker compose -f docker-compose.prod.yml up -d --build
```

### Access URLs:
- 🌐 **Frontend App**: `http://localhost:3000` (or `http://localhost:80` in production)
- ⚙️ **FastAPI OpenAPI Docs**: `http://localhost:8000/docs`
- 🏥 **Health Check**: `http://localhost:8000/health/ready`

---

## 💻 Local Development (Without Docker)

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate
pip install -e .[dev]

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Testing & Code Quality

### Run Pytest Suite (Unit, Scrapers & Integration Tests)
```bash
cd backend
pytest tests/ -v
```

### Run Ruff Code Quality Linter
```bash
cd backend
ruff check .
```

### Build Frontend
```bash
cd frontend
npm run build
```

---

## 📖 Documentation

Detailed documentation guides are available in `/docs`:
- 📐 [Architecture Overview](docs/architecture.md)
- 🕷️ [Scraper Development Guide](docs/scraper-development.md)
- 🔌 [REST API Reference](docs/api.md)
- 🚀 [Deployment Guide](docs/deployment.md)
- 📊 [Operations & Observability](docs/operations.md)
- 🔗 [n8n Integration Guide](docs/n8n-integration.md)

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for details.
