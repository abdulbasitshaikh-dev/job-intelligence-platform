from typing import Any, Dict, List, Optional

import httpx

from app.scrapers.base import BaseScraper, NormalizedJobData, RawJobData
from app.services.normalization import NormalizationService


class RemoteOKScraper(BaseScraper):
    """Real Public Source Adapter: RemoteOK JSON API."""

    def __init__(self, source_id: int, base_url: str = "https://remoteok.com/api", config: Dict[str, Any] = None, rate_limit_delay: float = 1.5):
        super().__init__(source_id, base_url or "https://remoteok.com/api", config or {}, rate_limit_delay)

    async def fetch(self) -> List[Any]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
            response = await client.get(self.base_url)
            response.raise_for_status()
            data = response.json()
            # RemoteOK first element is metadata legal notice
            if isinstance(data, list) and len(data) > 0 and "legal" in data[0]:
                return data[1:]
            return data if isinstance(data, list) else []

    @staticmethod
    def _safe_float(val: Any) -> Optional[float]:
        if val is None or val == "":
            return None
        try:
            if isinstance(val, (int, float)):
                return float(val)
            import re
            cleaned = re.sub(r"[^\d.]", "", str(val))
            return float(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None

    def parse(self, item: Any) -> RawJobData:
        if not isinstance(item, dict):
            item = {}

        ext_id = str(item.get("id", item.get("slug", "unk")))
        title = item.get("position", item.get("title", "Software Engineer"))
        company = item.get("company", "Remote Company")
        location = item.get("location", "Remote")
        description = item.get("description", title)
        url = item.get("url", f"https://remoteok.com/remote-jobs/{ext_id}")

        salary_min = self._safe_float(item.get("salary_min"))
        salary_max = self._safe_float(item.get("salary_max"))

        tags = item.get("tags", [])
        if isinstance(tags, list) and len(tags) > 0:
            description += f"\nSkills: {', '.join(tags)}"

        return RawJobData(
            external_id=ext_id,
            title=title,
            company=company,
            location=location,
            description=description,
            url=url,
            work_mode="Remote",
            salary_min=salary_min,
            salary_max=salary_max,
            currency="USD",
            raw_payload=item,
        )

    def normalize(self, raw_job: RawJobData) -> NormalizedJobData:
        return NormalizationService.normalize_raw_job(self.source_id, raw_job)
