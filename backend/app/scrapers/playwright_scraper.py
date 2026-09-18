import asyncio
from typing import Any, Dict, List
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.config import settings
from app.core.logging import logger
from app.scrapers.base import BaseScraper, RawJobData, NormalizedJobData
from app.services.normalization import NormalizationService


class PlaywrightScraper(BaseScraper):
    """Playwright Chromium Browser Scraper for JavaScript dynamic rendering."""

    def __init__(self, source_id: int, base_url: str, config: Dict[str, Any], rate_limit_delay: float = 1.5):
        super().__init__(source_id, base_url, config, rate_limit_delay)
        self.headless = config.get("headless", settings.PLAYWRIGHT_HEADLESS)
        self.timeout = config.get("timeout", settings.SCRAPE_REQUEST_TIMEOUT * 1000)
        self.wait_selector = config.get("wait_selector", "body")

    async def fetch(self) -> List[Any]:
        """Launch Playwright browser context, navigate to page, wait for rendering, and retrieve DOM."""
        await asyncio.sleep(self.rate_limit_delay)
        rendered_html = ""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
            )
            page = await context.new_page()
            
            try:
                await page.goto(self.base_url, timeout=self.timeout, wait_until="domcontentloaded")
                await page.wait_for_selector(self.wait_selector, timeout=5000)
                rendered_html = await page.content()
            except Exception as e:
                logger.warning("Playwright navigation error", url=self.base_url, error=str(e))
                # Safely attempt to retrieve content even on partial timeout
                try:
                    rendered_html = await page.content()
                except Exception:
                    rendered_html = ""
            finally:
                await context.close()
                await browser.close()

        if not rendered_html:
            return []

        soup = BeautifulSoup(rendered_html, "lxml")
        selector = self.config.get("item_selector", ".job-card")
        items = soup.select(selector)
        return items

    def parse(self, item: Any) -> RawJobData:
        """Parse BeautifulSoup element extracted from rendered HTML."""
        ext_id = item.get("data-job-id") or item.get("id") or "pw-unk"
        title_el = item.select_one(self.config.get("title_selector", ".title, h2, h3"))
        company_el = item.select_one(self.config.get("company_selector", ".company, .company-name"))
        location_el = item.select_one(self.config.get("location_selector", ".location"))

        title = title_el.get_text(strip=True) if title_el else "Unknown Title"
        company = company_el.get_text(strip=True) if company_el else "Unknown Company"
        location = location_el.get_text(strip=True) if location_el else "Remote"

        return RawJobData(
            external_id=str(ext_id),
            title=title,
            company=company,
            location=location,
            description=f"{title} at {company}",
            url=self.base_url,
            raw_payload={"html": str(item)},
        )

    def normalize(self, raw_job: RawJobData) -> NormalizedJobData:
        return NormalizationService.normalize_raw_job(self.source_id, raw_job)
