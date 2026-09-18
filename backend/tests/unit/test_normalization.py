from app.models.job import EmploymentType, WorkMode
from app.services.normalization import NormalizationService


def test_clean_text():
    raw_html = "<p>  Hello <b>World</b>   </p>"
    cleaned = NormalizationService.clean_text(raw_html)
    assert cleaned == "Hello World"


def test_normalize_work_mode():
    assert NormalizationService.normalize_work_mode("Remote") == WorkMode.REMOTE
    assert NormalizationService.normalize_work_mode(None, "Work from home Python Developer") == WorkMode.REMOTE
    assert NormalizationService.normalize_work_mode("Hybrid") == WorkMode.HYBRID
    assert NormalizationService.normalize_work_mode("On-site") == WorkMode.ON_SITE
    assert NormalizationService.normalize_work_mode(None, "Software Engineer") == WorkMode.UNSPECIFIED


def test_normalize_employment_type():
    assert NormalizationService.normalize_employment_type("Full-time") == EmploymentType.FULL_TIME
    assert NormalizationService.normalize_employment_type("Contract") == EmploymentType.CONTRACT
    assert NormalizationService.normalize_employment_type("Internship") == EmploymentType.INTERNSHIP


def test_normalize_url():
    raw_url = "https://example.com/jobs/123?utm_source=google&ref=123"
    cleaned = NormalizationService.normalize_url(raw_url)
    assert cleaned == "https://example.com/jobs/123"


def test_dedupe_hash_consistency():
    hash1 = NormalizationService.compute_dedupe_hash(1, "Python Developer", "TechCorp", "Remote")
    hash2 = NormalizationService.compute_dedupe_hash(1, "python developer ", "techcorp", " remote")
    assert hash1 == hash2
    assert len(hash1) == 64
