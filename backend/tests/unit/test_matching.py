from app.models.job import Job, EmploymentType, WorkMode
from app.models.user import JobPreference
from app.services.matching import MatchingService


def test_matching_score_calculation():
    job = Job(
        id=1,
        source_id=1,
        external_id="101",
        title="Senior Python Backend Developer",
        company="TechCorp",
        location="Pakistan",
        description="We are hiring a Python FastAPI developer to build microservices.",
        url="https://example.com/job/101",
        canonical_url="https://example.com/job/101",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.REMOTE,
        dedupe_hash="hash101",
        raw_data={},
    )

    preference = JobPreference(
        user_id=42,
        keywords=["Python", "FastAPI", "Backend"],
        locations=["Pakistan", "Remote"],
        employment_types=["Full-time"],
        work_modes=["Remote"],
    )

    result = MatchingService.calculate_match_score(job, preference)

    # Keywords (45) + Location (25) + Work Mode (20) + Employment (10) = 100
    assert result.total_score >= 80
    assert len(result.reasons) > 0
    assert result.user_id == 42
