import pytest
from unittest.mock import AsyncMock, patch
from app.scrapers.sources.remote_ok import RemoteOKScraper
from app.scrapers.sources.arbeitnow import ArbeitnowScraper


MOCK_REMOTEOK_ITEMS = [
    {
        "id": "12345",
        "slug": "remote-senior-python-engineer-techcorp-12345",
        "position": "Senior Python Engineer",
        "company": "TechCorp",
        "location": "Remote",
        "description": "Build APIs with FastAPI and PostgreSQL.",
        "url": "https://remoteok.com/remote-jobs/remote-senior-python-engineer-techcorp-12345",
        "tags": ["python", "fastapi", "postgresql"],
        "salary_min": 80000,
        "salary_max": 120000,
        "epoch": 1700000000,
    }
]

MOCK_ARBEITNOW_ITEMS = [
    {
        "slug": "backend-engineer-london-abc123",
        "company_name": "Acme Ltd",
        "title": "Backend Engineer",
        "description": "Python / Django / PostgreSQL backend developer.",
        "remote": False,
        "url": "https://www.arbeitnow.com/jobs/companies/acme-ltd/backend-engineer-london-abc123",
        "tags": ["Python", "Django"],
        "job_types": ["full-time"],
        "location": "London",
        "created_at": 1700000000,
    }
]


@pytest.mark.asyncio
async def test_remoteok_scraper_normalizes_correctly():
    """RemoteOK scraper: fetch → parse → normalize produces valid NormalizedJobData."""
    scraper = RemoteOKScraper(source_id=2)

    with patch.object(scraper, "fetch", new=AsyncMock(return_value=MOCK_REMOTEOK_ITEMS)):
        normalized_jobs = await scraper.run()

    assert len(normalized_jobs) == 1
    job = normalized_jobs[0]
    assert job.source_id == 2
    assert job.title == "Senior Python Engineer"
    assert job.company == "TechCorp"
    assert job.work_mode.value in ("REMOTE", "Remote")  # normalized enum
    assert job.salary_min == 80000
    assert job.salary_max == 120000
    assert job.dedupe_hash is not None
    assert len(job.dedupe_hash) == 64  # SHA-256 hex


@pytest.mark.asyncio
async def test_arbeitnow_scraper_normalizes_correctly():
    """Arbeitnow scraper: fetch → parse → normalize produces valid NormalizedJobData."""
    scraper = ArbeitnowScraper(source_id=3)

    with patch.object(scraper, "fetch", new=AsyncMock(return_value=MOCK_ARBEITNOW_ITEMS)):
        normalized_jobs = await scraper.run()

    assert len(normalized_jobs) == 1
    job = normalized_jobs[0]
    assert job.source_id == 3
    assert job.title == "Backend Engineer"
    assert job.company == "Acme Ltd"
    assert job.location == "London"
    assert job.dedupe_hash is not None


@pytest.mark.asyncio
async def test_scraper_deduplication_on_same_title_company_location():
    """Scrapers with identical title/company/location produce the same dedupe_hash."""
    scraper = RemoteOKScraper(source_id=2)
    item_a = dict(MOCK_REMOTEOK_ITEMS[0])
    item_b = dict(MOCK_REMOTEOK_ITEMS[0])
    item_b["id"] = "99999"  # Different ID, same content

    with patch.object(scraper, "fetch", new=AsyncMock(return_value=[item_a, item_b])):
        jobs = await scraper.run()

    assert len(jobs) == 2
    assert jobs[0].dedupe_hash == jobs[1].dedupe_hash  # Same hash → deduplication candidate
