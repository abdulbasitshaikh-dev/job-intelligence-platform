FROM python:3.12-slim AS base

# Set working directory & environment
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies (no playwright here - it's 48MB + browser binaries)
COPY pyproject.toml /app/
RUN pip install --upgrade pip && \
    pip install setuptools && \
    pip install -e .

# Copy backend application source
COPY . /app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Worker stage: extends base with Playwright for browser-based scraping ──
FROM base AS worker
RUN pip install -e ".[scraping]" && \
    playwright install chromium --with-deps || true
CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info"]
