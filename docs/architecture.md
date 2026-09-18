# System Architecture - Job Intelligence Platform

## Modular Monolith Blueprint

The Job Intelligence Platform is engineered as a **Modular Monolith** using Python 3.12+ and FastAPI. Rather than incurring microservices network overhead, domain logic is partitioned into clean, decoupled modules (`auth`, `users`, `jobs`, `sources`, `scrapers`, `matching`, `notifications`, `applications`, `tasks`).

```
                              +---------------------------------+
                              |        FRONTEND DASHBOARD       |
                              |   (Next.js / React + Tailwind)  |
                              +----------------+----------------+
                                               |
                                               v (REST API / JWT)
                              +---------------------------------+
                              |          FASTAPI API            |
                              +----------------+----------------+
                                               |
                     +-------------------------+-------------------------+
                     |                         |                         |
                     v                         v                         v
           +-------------------+     +-------------------+     +-------------------+
           |    Auth & Users   |     | Job Feed & Search |     | Admin & Telemetry |
           +-------------------+     +-------------------+     +-------------------+
                     |                         |                         |
                     +-------------------------+-------------------------+
                                               |
                                               v
                              +---------------------------------+
                              |    PostgreSQL 16 DATABASE       |
                              |  (Jobs, Sources, ScraperRuns)   |
                              +----------------+----------------+
                                               ^
                                               | (ORM sync session)
                              +----------------+----------------+
                              |    CELERY BACKGROUND WORKERS    |
                              |      Redis Broker / Beat        |
                              +----------------+----------------+
                                               |
                                               v
                              +---------------------------------+
                              |         SCRAPER ENGINE          |
                              |  (HTTP, API, Playwright Chrome) |
                              +---------------------------------+
```

## Key Ingestion & Normalization Flow

1. **Scraping**: `Celery Beat` periodically executes `scrape_all_sources_task`. Each source runs inside an isolated task frame with error handling.
2. **Parsing & Normalization**: Raw HTML/JSON is passed into `BaseScraper.parse() -> RawJobData` and converted by `NormalizationService` into canonical `NormalizedJobData`.
3. **Multi-tier Deduplication**: `DeduplicationService` computes SHA256 hashes of `normalized(title) + normalized(company) + normalized(location)` and checks against canonical URLs and external IDs.
4. **Deterministic Match Engine**: Computes explainable match scores (0–100%) against configured user preferences (keywords, location, work mode, salary).
5. **Event-Driven Webhook Dispatch**: Webhook emitters dispatch structured JSON payloads compatible with n8n workflow triggers.
