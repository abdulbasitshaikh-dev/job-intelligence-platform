import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse
from typing import Optional, Tuple

from app.models.job import EmploymentType, WorkMode
from app.scrapers.base import RawJobData, NormalizedJobData


class NormalizationService:
    """Service to clean, standardize, and hash scraped raw job data into canonical schema."""

    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """Strip HTML tags, decode entities, and normalize whitespace."""
        if not text:
            return ""
        # Remove simple HTML tags
        clean = re.sub(r"<[^>]+>", " ", text)
        # Collapse multiple spaces and newlines
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @staticmethod
    def normalize_company(company: str) -> str:
        """Standardize company name."""
        clean = NormalizationService.clean_text(company)
        # Remove common suffixes if appropriate or lowercase comparison
        return clean or "Unknown Company"

    @staticmethod
    def normalize_work_mode(work_mode_str: Optional[str], text_content: str = "") -> WorkMode:
        """Infer work mode enum from explicit string or content text."""
        combined = f"{work_mode_str or ''} {text_content}".lower()
        if "remote" in combined or "work from home" in combined or "wfh" in combined or "anywhere" in combined:
            return WorkMode.REMOTE
        elif "hybrid" in combined or "flexible" in combined:
            return WorkMode.HYBRID
        elif "on-site" in combined or "onsite" in combined or "in-office" in combined:
            return WorkMode.ON_SITE
        return WorkMode.UNSPECIFIED

    @staticmethod
    def normalize_employment_type(emp_str: Optional[str], text_content: str = "") -> EmploymentType:
        """Infer employment type enum from explicit string or content text."""
        combined = f"{emp_str or ''} {text_content}".lower()
        if "full-time" in combined or "full time" in combined or "permanent" in combined:
            return EmploymentType.FULL_TIME
        elif "part-time" in combined or "part time" in combined:
            return EmploymentType.PART_TIME
        elif "contract" in combined or "freelance" in combined or "consultant" in combined:
            return EmploymentType.CONTRACT
        elif "intern" in combined or "trainee" in combined:
            return EmploymentType.INTERNSHIP
        elif "temp" in combined or "temporary" in combined:
            return EmploymentType.TEMPORARY
        return EmploymentType.FULL_TIME

    @staticmethod
    def normalize_url(url: str) -> str:
        """Produce clean canonical URL by stripping tracking parameters (utm_*, ref, etc.)."""
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            # Remove tracking params
            filtered_query = "&".join(
                param for param in parsed.query.split("&")
                if not any(param.startswith(prefix) for prefix in ["utm_", "ref=", "fbclid=", "gclid="])
            )
            canonical = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, filtered_query, ""))
            return canonical.rstrip("/")
        except Exception:
            return url.rstrip("/")

    @staticmethod
    def compute_dedupe_hash(source_id: int, title: str, company: str, location: str) -> str:
        """Compute SHA256 deduplication hash based on normalized title, company, and location."""
        raw_key = f"{source_id}:{title.lower().strip()}:{company.lower().strip()}:{location.lower().strip()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def normalize_raw_job(cls, source_id: int, raw: RawJobData) -> NormalizedJobData:
        """Transform raw scraped data into clean NormalizedJobData."""
        title = cls.clean_text(raw.title)
        company = cls.normalize_company(raw.company)
        location = cls.clean_text(raw.location) or "Remote"
        description = cls.clean_text(raw.description)
        canonical_url = cls.normalize_url(raw.url)

        work_mode = cls.normalize_work_mode(raw.work_mode, f"{title} {description}")
        employment_type = cls.normalize_employment_type(raw.employment_type, f"{title} {description}")

        dedupe_hash = cls.compute_dedupe_hash(source_id, title, company, location)

        return NormalizedJobData(
            source_id=source_id,
            external_id=str(raw.external_id),
            title=title,
            company=company,
            location=location,
            description=description,
            url=raw.url,
            canonical_url=canonical_url,
            employment_type=employment_type,
            work_mode=work_mode,
            salary_min=raw.salary_min,
            salary_max=raw.salary_max,
            currency=raw.currency or "USD",
            posted_at=raw.posted_at or datetime.now(timezone.utc),
            dedupe_hash=dedupe_hash,
            raw_data=raw.raw_payload,
        )
