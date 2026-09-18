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
                reasons=[MatchReason(category="Default", points=0, description="No preferences configured")],
            )

        job_title_lower = job.title.lower()
        job_desc_lower = job.description.lower()
        job_loc_lower = job.location.lower()

        # 1. Keywords (up to 45 pts)
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

        kw_total = min(45, kw_title_score + kw_desc_score)
        if kw_total > 0:
            total_score += kw_total
            reasons.append(
                MatchReason(
                    category="Keywords",
                    points=kw_total,
                    description=f"Matched keywords: {', '.join(matched_keywords)}",
                )
            )

        # 2. Location (up to 25 pts)
        location_matched = False
        for loc in preference.locations or []:
            loc_clean = loc.lower().strip()
            if not loc_clean:
                continue
            if loc_clean in job_loc_lower or ("remote" in loc_clean and job.work_mode.value.lower() == "remote"):
                location_matched = True
                reasons.append(
                    MatchReason(
                        category="Location",
                        points=25,
                        description=f"Matched preferred location: {loc}",
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
                        description=f"Matched work mode preference: {job.work_mode.value}",
                    )
                )

        # 4. Employment Type (up to 10 pts)
        if preference.employment_types:
            pref_emp = [e.lower() for e in preference.employment_types]
            if job.employment_type.value.lower() in pref_emp:
                total_score += 10
                reasons.append(
                    MatchReason(
                        category="Employment Type",
                        points=10,
                        description=f"Matched employment type: {job.employment_type.value}",
                    )
                )

        final_score = min(100, total_score)
        return MatchScoreResponse(
            job_id=job.id,
            user_id=preference.user_id,
            total_score=final_score,
            reasons=reasons,
        )
