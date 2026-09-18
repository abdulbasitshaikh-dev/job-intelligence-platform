# Operations & Observability Guide

## 1. Monitoring System Health

- **Liveness Probe**: `GET /health/live`
- **Readiness Probe**: `GET /health/ready` (Verifies PostgreSQL & Redis connections)

## 2. Celery Worker Telemetry

To inspect running Celery background worker tasks:

```bash
docker compose exec worker celery -A app.celery_app.celery_app status
```

## 3. Scraper Run Telemetry Logs

Scraper execution performance and error traces are persistently recorded in the `scraper_runs` table.
Query via Admin API: `GET /api/v1/admin/scraper-runs` or view in the Admin Dashboard tab.

## 4. Manual Scrape Execution

Trigger an immediate background scrape run for source ID 1:

```bash
curl -X POST http://localhost:8000/api/v1/admin/sources/1/scrape \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>"
```
