import asyncio
from typing import Any, Dict, List, Optional
import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.core.logging import logger
from app.scrapers.base import BaseScraper, RawJobData, NormalizedJobData
from app.services.normalization import NormalizationService


class HTTPScraper(BaseScraper):
    """Generic HTTP HTML scraper supporting timeouts, retry backoff, headers, and parsing."""

    def __init__(self, source_id: int, base_url: str, config: Dict[str, Any], rate_limit_delay: float = 1.5):
        super().__init__(source_id, base_url, config, rate_limit_delay)
        self.headers = config.get(
            "headers",
            {
                "User-Agent": "JobIntelligencePlatform/1.0 (+https://github.com/job-intelligence)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        self.timeout = config.get("timeout", settings.SCRAPE_REQUEST_TIMEOUT)

    async def fetch_html(self, url: str) -> str:
        """Fetch HTML content with retries and timeout."""
        retries = 3
        backoff = 2.0
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.text
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                logger.warning(
                    "HTTP fetch attempt failed",
                    url=url,
                    attempt=attempt + 1,
                    error=str(e),
                )
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(backoff * (attempt + 1))
        return ""

    async def fetch(self) -> List[Any]:
        """Fetch HTML page and extract raw items using BeautifulSoup."""
        await asyncio.sleep(self.rate_limit_delay)
        html = await self.fetch_html(self.base_url)
        soup = BeautifulSoup(html, "lxml")
        selector = self.config.get("item_selector", ".job-item")
        items = soup.select(selector)
        return items

    def parse(self, item: Any) -> RawJobData:
        """Parse BeautifulSoup element using configured selectors."""
        ext_id_attr = self.config.get("external_id_attr", "data-id")
        external_id = item.get(ext_id_attr) or item.get("id") or "unk"
        
        title_el = item.select_one(self.config.get("title_selector", ".title"))
        title = title_el.get_text(strip=True) if title_el else "Unknown Title"

        company_el = item.select_one(self.config.get("company_selector", ".company"))
        company = company_el.get_text(strip=True) if company_el else "Unknown Company"

        location_el = item.select_one(self.config.get("location_selector", ".location"))
        location = location_el.get_text(strip=True) if location_el else "Remote"

        desc_el = item.select_one(self.config.get("description_selector", ".description"))
        description = desc_el.get_text(strip=True) if desc_el else title

        link_el = item.select_one(self.config.get("link_selector", "a"))
        url = link_el.get("href", "") if link_el else self.base_url
        if url and not url.startswith("http"):
            url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"

        return RawJobData(
            external_id=str(external_id),
            title=title,
            company=company,
            location=location,
            description=description,
            url=url or self.base_url,
            raw_payload={"html": str(item)},
        )

    def normalize(self, raw_job: RawJobData) -> NormalizedJobData:
        return NormalizationService.normalize_raw_job(self.source_id, raw_job)
