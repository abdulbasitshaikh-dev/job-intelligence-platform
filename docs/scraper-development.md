# Scraper Development Guide

This guide details how to add a new job source scraper adapter to the Job Intelligence Platform.

## 1. Implement `BaseScraper`

Create a new file under `backend/app/scrapers/sources/your_source.py`:

```python
from typing import Any, Dict, List
import httpx
from app.scrapers.base import BaseScraper, RawJobData, NormalizedJobData
from app.services.normalization import NormalizationService

class MySourceScraper(BaseScraper):
    async def fetch(self) -> List[Any]:
        # Fetch items from endpoint
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(self.base_url)
            return res.json().get("jobs", [])

    def parse(self, item: Any) -> RawJobData:
        return RawJobData(
            external_id=str(item["id"]),
            title=item["title"],
            company=item["company"],
            location=item["location"],
            description=item["description"],
            url=item["url"],
            work_mode="Remote",
            raw_payload=item,
        )

    def normalize(self, raw_job: RawJobData) -> NormalizedJobData:
        return NormalizationService.normalize_raw_job(self.source_id, raw_job)
```

## 2. Register in Scraper Registry

In `backend/app/scrapers/sources/scraper_registry.py`:

```python
from app.scrapers.sources.your_source import MySourceScraper

SCRAPER_REGISTRY = {
    "my_source_key": MySourceScraper,
    # ...
}
```

## 3. Register Source via Admin API or DB Seed

Submit `POST /api/v1/admin/sources`:

```json
{
  "name": "My Custom Source",
  "base_url": "https://api.example.com/jobs",
  "source_type": "API",
  "scraper_type": "my_source_key",
  "enabled": true,
  "rate_limit_delay": 1.5
}
```
