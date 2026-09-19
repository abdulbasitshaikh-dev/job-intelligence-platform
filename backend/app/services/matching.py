import re
from typing import List, Optional

from app.models.job import Job
from app.models.user import JobPreference
from app.schemas.job import MatchReason, MatchScoreResponse

# Non-geographic location tokens to exclude from geographic location matching
NON_GEOGRAPHIC_TOKENS = {
    "remote",
    "anywhere",
    "worldwide",
    "wfh",
    "work from home",
    "global",
    "telecommute",
}


def match_keyword_token(kw: str, text: str) -> bool:
    """Robust keyword matching with word-boundaries that preserves technical symbols.

    Prevents false positives:
      - 'Go' does not match 'good' or 'Google'
      - 'C' does not match 'customer' or 'cloud'
      - 'Java' does not match 'JavaScript'
      - 'R' does not match 'remote'

    Supports technical keywords:
      - 'C++', 'C#', '.NET', 'Node.js', 'Next.js', 'React Native', 'FastAPI', 'PostgreSQL'
    """
    if not kw or not text:
        return False

    k = kw.strip().lower()
    t = text.lower()

    if not k or not t:
        return False

    # Specific technical keyword patterns
    if k in ("c++", "cpp"):
        return bool(re.search(r"(?:^|[^\w+])c\+\+(?:[^\w+]|$)", t))
    if k in ("c#", "csharp"):
        return bool(re.search(r"(?:^|[^\w#])c#(?:[^\w#]|$)", t))
    if k in (".net", "dotnet"):
        return bool(re.search(r"(?:^|[^\w])(?:\.net|dotnet)(?:[^\w]|$)", t))
    if k in ("node.js", "nodejs"):
        return bool(re.search(r"\b(?:node\.js|nodejs)\b", t))
    if k in ("next.js", "nextjs"):
        return bool(re.search(r"\b(?:next\.js|nextjs)\b", t))
    if k == "react native":
        return bool(re.search(r"\breact\s+native\b", t))
    if k == "react":
        # Match 'react' as standalone word, but exclude 'react native' if matched separately
        return bool(re.search(r"\breact\b", t))
    if k in ("postgresql", "postgres"):
        return bool(re.search(r"\b(?:postgresql|postgres)\b", t))
    if k == "c":
        # Single letter 'c' must not be followed by '+' or '#'
        return bool(re.search(r"(?:^|[^\w+#])c(?:[^\w+#]|$)", t))
    if k == "r":
        # Single letter 'r'
        return bool(re.search(r"(?:^|[^\w])r(?:[^\w]|$)", t))

    # General word-boundary pattern for multi-character terms
    pattern = r"\b" + re.escape(k) + r"\b"
    return bool(re.search(pattern, t))


class MatchingService:
    """Deterministic, Explainable Job Preference Matching Engine."""

    @staticmethod
    def has_meaningful_preferences(preference: Optional[JobPreference]) -> bool:
        """Check if preference contains at least one user-specified filter."""
        if not preference:
            return False
        return bool(
            (preference.keywords and len(preference.keywords) > 0)
            or (preference.locations and len(preference.locations) > 0)
            or (preference.work_modes and len(preference.work_modes) > 0)
            or (preference.employment_types and len(preference.employment_types) > 0)
            or preference.min_salary is not None
            or preference.max_salary is not None
        )

    @staticmethod
    def calculate_match_score(job: Job, preference: Optional[JobPreference]) -> MatchScoreResponse:
        total_score = 0
        reasons: List[MatchReason] = []

        if not preference or not MatchingService.has_meaningful_preferences(preference):
            return MatchScoreResponse(
                job_id=job.id,
                user_id=preference.user_id if preference else 0,
                total_score=0,
                reasons=[
                    MatchReason(
                        category="Preferences",
                        points=0,
                        description="Set preferences to see your match score.",
                    )
                ],
            )

        job_title = job.title or ""
        job_desc = job.description or ""
        job_loc_lower = (job.location or "").lower()

        # 1. Keywords / Role relevance (up to 40 pts)
        # Title match: +25 pts per keyword
        # Description match: +15 pts per keyword
        kw_title_score = 0
        kw_desc_score = 0
        matched_keywords = []

        configured_keywords = [k.strip() for k in (preference.keywords or []) if k.strip()]

        for kw in configured_keywords:
            if match_keyword_token(kw, job_title):
                kw_title_score += 25
                matched_keywords.append(f"{kw} (in title)")
            elif match_keyword_token(kw, job_desc):
                kw_desc_score += 15
                matched_keywords.append(f"{kw} (in description)")

        kw_total = min(40, kw_title_score + kw_desc_score)
        if kw_total > 0:
            total_score += kw_total
            reasons.append(
                MatchReason(
                    category="Skills",
                    points=kw_total,
                    description=f"+{kw_total} {', '.join(matched_keywords)} match",
                )
            )

        # 2. Location (up to 20 pts)
        # Must evaluate actual physical/geographical locations only (e.g. country, city, region)
        # 'Remote' is strictly evaluated under Work Mode to prevent double-counting.
        geographic_locations = [
            loc.strip() for loc in (preference.locations or [])
            if loc.strip() and loc.strip().lower() not in NON_GEOGRAPHIC_TOKENS
        ]

        for loc in geographic_locations:
            loc_clean = loc.lower()
            if loc_clean in job_loc_lower:
                reasons.append(
                    MatchReason(
                        category="Location",
                        points=20,
                        description=f"+20 Preferred location match: {loc}",
                    )
                )
                total_score += 20
                break

        # 3. Work Mode (up to 20 pts)
        # Evaluates Remote, Hybrid, On-site
        if preference.work_modes:
            pref_modes = [m.lower().strip() for m in preference.work_modes if m.strip()]
            job_mode = job.work_mode.value.lower() if hasattr(job.work_mode, "value") else str(job.work_mode).lower()
            if job_mode in pref_modes or "unspecified" in pref_modes:
                total_score += 20
                reasons.append(
                    MatchReason(
                        category="Work Mode",
                        points=20,
                        description=f"+20 {job.work_mode.value} work mode matches",
                    )
                )

        # 4. Employment Type (up to 10 pts)
        if preference.employment_types:
            pref_emp = [e.lower().strip() for e in preference.employment_types if e.strip()]
            job_emp = job.employment_type.value.lower() if hasattr(job.employment_type, "value") else str(job.employment_type).lower()
            if job_emp in pref_emp:
                total_score += 10
                reasons.append(
                    MatchReason(
                        category="Employment",
                        points=10,
                        description=f"+10 {job.employment_type.value} employment matches",
                    )
                )

        # 5. Salary Compatibility (up to 10 pts)
        if preference.min_salary is not None or preference.max_salary is not None:
            user_min = float(preference.min_salary or 0)
            user_max = float(preference.max_salary or 10_000_000)
            job_min = float(job.salary_min) if job.salary_min is not None else None
            job_max = float(job.salary_max) if job.salary_max is not None else None

            if job_min is not None or job_max is not None:
                effective_job_min = job_min if job_min is not None else (job_max or 0)
                effective_job_max = job_max if job_max is not None else (job_min or 10_000_000)

                # Overlap test: [effective_job_min, effective_job_max] overlaps [user_min, user_max]
                if effective_job_max >= user_min and effective_job_min <= user_max:
                    total_score += 10
                    reasons.append(
                        MatchReason(
                            category="Salary",
                            points=10,
                            description="+10 Salary range compatible with your target compensation",
                        )
                    )

        # 6. Role/Skill Relevance Gating
        # Invariant: If user defined technical/role keywords, but a job matches ZERO keywords,
        # generic attributes (e.g. Remote + Full-time) cannot produce a misleadingly high match score.
        if len(configured_keywords) > 0 and kw_total == 0:
            if total_score > 15:
                total_score = min(15, total_score // 2)
                reasons.append(
                    MatchReason(
                        category="Role Relevance",
                        points=0,
                        description="Score capped: No matching target skills/keywords found for this role",
                    )
                )

        final_score = max(0, min(100, total_score))
        return MatchScoreResponse(
            job_id=job.id,
            user_id=preference.user_id,
            total_score=final_score,
            reasons=reasons,
        )
