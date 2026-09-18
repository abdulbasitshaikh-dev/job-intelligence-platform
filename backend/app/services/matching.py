from typing import List

from app.models.job import Job
from app.models.user import JobPreference
from app.schemas.job import MatchReason, MatchScoreResponse


class MatchingService:
    """Deterministic Job Preference Matching Engine."""

    @staticmethod
    def calculate_match_score(job: Job, preference: JobPreference) -> MatchScoreResponse:
        total_score = 0
        reasons: List[MatchReason] = []

        if not preference:
            return MatchScoreResponse(
                job_id=job.id,
                user_id=0,
                total_score=0,
                reasons=[MatchReason(category="Default", points=0, description="Set preferences to see your match score.")],
            )

        has_any_pref = bool(
            (preference.keywords and len(preference.keywords) > 0)
            or (preference.locations and len(preference.locations) > 0)
            or (preference.work_modes and len(preference.work_modes) > 0)
            or (preference.employment_types and len(preference.employment_types) > 0)
            or preference.min_salary
            or preference.max_salary
        )

        if not has_any_pref:
            return MatchScoreResponse(
                job_id=job.id,
                user_id=preference.user_id,
                total_score=0,
                reasons=[MatchReason(category="Preferences", points=0, description="Set preferences to see your match score.")],
            )

        job_title_lower = (job.title or "").lower()
        job_desc_lower = (job.description or "").lower()
        job_loc_lower = (job.location or "").lower()

        # 1. Keywords (up to 35 pts)
        kw_title_score = 0
        kw_desc_score = 0
        matched_keywords = []

        for kw in preference.keywords or []:
            kw_clean = kw.lower().strip()
            if not kw_clean:
                continue
            if kw_clean in job_title_lower:
                kw_title_score += 20
                matched_keywords.append(f"{kw} (in title)")
            elif kw_clean in job_desc_lower:
                kw_desc_score += 10
                matched_keywords.append(f"{kw} (in description)")

        kw_total = min(35, kw_title_score + kw_desc_score)
        if kw_total > 0:
            total_score += kw_total
            reasons.append(
                MatchReason(
                    category="Skills",
                    points=kw_total,
                    description=f"+{kw_total} {', '.join(matched_keywords)} match",
                )
            )

        # 2. Location (up to 25 pts)
        for loc in preference.locations or []:
            loc_clean = loc.lower().strip()
            if not loc_clean:
                continue
            if loc_clean in job_loc_lower or ("remote" in loc_clean and job.work_mode.value.lower() == "remote"):
                reasons.append(
                    MatchReason(
                        category="Location",
                        points=25,
                        description=f"+25 Preferred location match: {loc}",
                    )
                )
                total_score += 25
                break

        # 3. Work Mode (up to 20 pts)
        if preference.work_modes:
            pref_modes = [m.lower() for m in preference.work_modes]
            if job.work_mode.value.lower() in pref_modes or "unspecified" in pref_modes:
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
            pref_emp = [e.lower() for e in preference.employment_types]
            if job.employment_type.value.lower() in pref_emp:
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

        final_score = min(100, total_score)
        return MatchScoreResponse(
            job_id=job.id,
            user_id=preference.user_id,
            total_score=final_score,
            reasons=reasons,
        )

