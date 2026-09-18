from app.scrapers.api_scraper import APIScraper
from app.scrapers.base import BaseScraper, NormalizedJobData, RawJobData
from app.scrapers.http_scraper import HTTPScraper

# Playwright is an optional dependency; gracefully degrade if not installed
try:
    from app.scrapers.playwright_scraper import PlaywrightScraper
except ImportError:
    PlaywrightScraper = None  # type: ignore[assignment,misc]

from app.scrapers.sources.scraper_registry import SCRAPER_REGISTRY, get_scraper_class

__all__ = [
    "BaseScraper",
    "RawJobData",
    "NormalizedJobData",
    "HTTPScraper",
    "APIScraper",
    "PlaywrightScraper",
    "SCRAPER_REGISTRY",
    "get_scraper_class",
]
