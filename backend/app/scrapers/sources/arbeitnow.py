from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx

from app.scrapers.base import BaseScraper, NormalizedJobData, RawJobData
from app.services.normalization import NormalizationService


class ArbeitnowScraper(BaseScraper):
    """Real Public Source Adapter: Arbeitnow Job Board API."""

    def __init__(self, source_id: int, base_url: str = "https://www.arbeitnow.com/api/job-board-api", config: Dict[str, Any] = None, rate_limit_delay: float = 1.5):
        super().__init__(source_id, base_url or "https://www.arbeitnow.com/api/job-board-api", config or {}, rate_limit_delay)

    async def fetch(self) -> List[Any]:
        headers = {
            "User-Agent": "JobIntelPlatform/1.0 (Production Job Aggregator)",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
            response = await client.get(self.base_url)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])

    def parse(self, item: Any) -> RawJobData:
        if not isinstance(item, dict):
            item = {}

        slug = str(item.get("slug") or item.get("id") or "")
        title = item.get("title") or "Software Engineer"
        company = item.get("company_name") or "Tech Company"
        location = item.get("location") or "Remote"
        url = item.get("url") or f"https://www.arbeitnow.com/jobs/{slug}"
        description = item.get("description") or title

        tags = item.get("tags") or []
        if isinstance(tags, list) and tags:
            description += f"\nRequired Skills: {', '.join(tags)}"

        is_remote = item.get("remote", False)
        work_mode = "Remote" if is_remote else ("Hybrid" if "hybrid" in str(location).lower() else "On-site")

        # Parse posted_at timestamp
        created_at = item.get("created_at")
        posted_at = None
        if created_at:
            try:
                if isinstance(created_at, (int, float)):
                    posted_at = datetime.fromtimestamp(created_at, tz=timezone.utc)
            except Exception:
                posted_at = None

        raw_job = RawJobData(
            external_id=slug,
            title=title,
            company=company,
            location=location,
            description=description,
            url=url,
            work_mode=work_mode,
            employment_type="Full-time",
            currency="EUR",
            raw_payload=item,
        )
        if posted_at:
            raw_job.posted_at = posted_at

        return raw_job

    def normalize(self, raw_job: RawJobData) -> NormalizedJobData:
        return NormalizationService.normalize_raw_job(self.source_id, raw_job)
