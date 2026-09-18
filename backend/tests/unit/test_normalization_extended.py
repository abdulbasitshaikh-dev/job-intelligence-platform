import pytest

from app.scrapers.base import RawJobData
from app.services.normalization import NormalizationService


def test_normalize_location_deduplication():
    # Deduplicates repeated tokens like "California, California, US"
    loc = "California, California, US"
    cleaned = NormalizationService.normalize_location(loc)
    assert cleaned == "California, US"

    # Cleans extra commas and spaces
    loc2 = "  Berlin ,  , Germany  "
    assert NormalizationService.normalize_location(loc2) == "Berlin, Germany"

    # Handles None or empty string gracefully
    assert NormalizationService.normalize_location(None) == "Remote"
    assert NormalizationService.normalize_location("") == "Remote"


def test_normalize_salary_range():
    # Inverted range swapped
    s_min, s_max = NormalizationService.normalize_salary_range(120000, 80000)
    assert s_min == 80000
    assert s_max == 120000

    # Negative bounds discarded
    s_min2, s_max2 = NormalizationService.normalize_salary_range(-5000, 100000)
    assert s_min2 is None
    assert s_max2 == 100000

    # Normal range untouched
    s_min3, s_max3 = NormalizationService.normalize_salary_range(60000, 90000)
    assert s_min3 == 60000
    assert s_max3 == 90000


def test_validate_raw_job():
    valid = RawJobData(
        external_id="ext-1",
        title="Software Engineer",
        company="Acme Corp",
        location="Remote",
        description="Write clean code",
        url="https://example.com/job/1",
        source_id=1,
    )
    # Should not raise
    NormalizationService.validate_raw_job(valid)

    # Missing title raises ValueError
    invalid_title = RawJobData(
        external_id="ext-2",
        title="  ",
        company="Acme Corp",
        location="Remote",
        description="Write clean code",
        url="https://example.com/job/2",
        source_id=1,
    )
    with pytest.raises(ValueError, match="Job title is missing"):
        NormalizationService.validate_raw_job(invalid_title)

    # Missing company raises ValueError
    invalid_company = RawJobData(
        external_id="ext-3",
        title="Developer",
        company="",
        location="Remote",
        description="Write clean code",
        url="https://example.com/job/3",
        source_id=1,
    )
    with pytest.raises(ValueError, match="Company name is missing"):
        NormalizationService.validate_raw_job(invalid_company)

    # Invalid URL scheme raises ValueError
    invalid_url = RawJobData(
        external_id="ext-4",
        title="Developer",
        company="Acme Corp",
        location="Remote",
        description="Write clean code",
        url="javascript:alert(1)",
        source_id=1,
    )
    with pytest.raises(ValueError, match="Invalid job URL"):
        NormalizationService.validate_raw_job(invalid_url)
