import asyncio
from typing import Any, Dict, List
import httpx

from app.config import settings
from app.core.logging import logger
from app.scrapers.base import BaseScraper, RawJobData, NormalizedJobData
from app.services.normalization import NormalizationService


class APIScraper(BaseScraper):
    """API Ingestion Scraper for sources returning structured JSON."""

    def __init__(self, source_id: int, base_url: str, config: Dict[str, Any], rate_limit_delay: float = 1.5):
        super().__init__(source_id, base_url, config, rate_limit_delay)
        self.headers = config.get("headers", {"Accept": "application/json"})
        self.params = config.get("params", {})
        self.timeout = config.get("timeout", settings.SCRAPE_REQUEST_TIMEOUT)

    async def fetch(self) -> List[Any]:
        """Fetch JSON payload from API endpoint."""
        await asyncio.sleep(self.rate_limit_delay)
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            response = await client.get(self.base_url, params=self.params)
            response.raise_for_status()
            data = response.json()
            
            # Extract list from nested key if configured (e.g. data["jobs"])
            items_key = self.config.get("items_key")
            if items_key and isinstance(data, dict):
                return data.get(items_key, [])
            elif isinstance(data, list):
                return data
            return [data]

    def parse(self, raw_item: Any) -> RawJobData:
        """Parse JSON item dictionary using configured key mappings."""
        if not isinstance(raw_item, dict):
            raw_item = {"raw": str(raw_item)}

        id_key = self.config.get("id_key", "id")
        title_key = self.config.get("title_key", "title")
        company_key = self.config.get("company_key", "company")
        location_key = self.config.get("location_key", "location")
        desc_key = self.config.get("description_key", "description")
        url_key = self.config.get("url_key", "url")

        raw_id = raw_item.get(id_key) if raw_item.get(id_key) is not None else raw_item.get("id", "unk")
        external_id = str(raw_id)
        title = str(raw_item.get(title_key) or "Unknown Title")
        company = str(raw_item.get(company_key) or "Unknown Company")
        location = str(raw_item.get(location_key) or "Remote")
        description = str(raw_item.get(desc_key) or title)
        url = str(raw_item.get(url_key) or self.base_url)

        return RawJobData(
            external_id=external_id,
            title=title,
            company=company,
            location=location,
            description=description,
            url=url,
            raw_payload=raw_item if isinstance(raw_item, dict) else {},
        )

    def normalize(self, raw_job: RawJobData) -> NormalizedJobData:
        return NormalizationService.normalize_raw_job(self.source_id, raw_job)
