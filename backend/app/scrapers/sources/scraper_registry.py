from typing import Dict, Optional, Type

from app.scrapers.api_scraper import APIScraper
from app.scrapers.base import BaseScraper
from app.scrapers.http_scraper import HTTPScraper
from app.scrapers.sources.arbeitnow import ArbeitnowScraper
from app.scrapers.sources.remote_ok import RemoteOKScraper

# Playwright is an optional dependency
try:
    from app.scrapers.playwright_scraper import PlaywrightScraper
    _playwright_cls: Optional[Type[BaseScraper]] = PlaywrightScraper
except ImportError:
    _playwright_cls = None

SCRAPER_REGISTRY: Dict[str, Type[BaseScraper]] = {
    "remote_ok": RemoteOKScraper,
    "arbeitnow": ArbeitnowScraper,
    "http_generic": HTTPScraper,
    "api_generic": APIScraper,
}

if _playwright_cls is not None:
    SCRAPER_REGISTRY["playwright_generic"] = _playwright_cls


def get_scraper_class(scraper_type: str) -> Type[BaseScraper]:
    """Retrieve scraper class implementation from registry with safe fallback to APIScraper."""
    return SCRAPER_REGISTRY.get(scraper_type, APIScraper)
