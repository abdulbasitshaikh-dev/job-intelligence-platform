from app.models.job import EmploymentType, Job, WorkMode
from app.models.user import JobPreference
from app.services.matching import MatchingService, match_keyword_token


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
        locations=["Pakistan"],
        employment_types=["Full-time"],
        work_modes=["Remote"],
    )

    result = MatchingService.calculate_match_score(job, preference)

    # Keywords (40) + Location (20) + Work Mode (20) + Employment (10) = 90
    assert result.total_score >= 80
    assert len(result.reasons) > 0
    assert result.user_id == 42


def test_matching_empty_preferences_returns_zero():
    """Empty preferences must produce 0 score and neutral guidance reason."""
    job = Job(
        id=2,
        source_id=1,
        external_id="102",
        title="Senior Python Backend Developer",
        company="TechCorp",
        location="Pakistan",
        description="FastAPI role.",
        url="https://example.com/job/102",
        canonical_url="https://example.com/job/102",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.REMOTE,
        dedupe_hash="hash102",
        raw_data={},
    )

    empty_preference = JobPreference(
        user_id=99,
        keywords=[],
        locations=[],
        employment_types=[],
        work_modes=[],
        min_salary=None,
        max_salary=None,
    )

    assert not MatchingService.has_meaningful_preferences(empty_preference)
    result = MatchingService.calculate_match_score(job, empty_preference)
    assert result.total_score == 0
    assert any("Set preferences" in r.description for r in result.reasons)


def test_critical_unrelated_job_does_not_score_55():
    """Critical Case: Healthcare nursing job in Philippines must NOT receive 55%

    for a user with Python/FastAPI/Pakistan/Remote preferences.
    """
    nurse_job = Job(
        id=316,
        source_id=2,
        external_id="ext-316",
        title="Healthcare Virtual Assistant Registered Nurse",
        company="Snapscale",
        location="Davao, Davao Region, Philippines",
        description="Nursing and clinical coordination tasks for healthcare clinics.",
        url="https://example.com/jobs/nurse",
        canonical_url="https://example.com/jobs/nurse",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.REMOTE,
        dedupe_hash="hash-nurse",
        raw_data={},
    )

    dev_preference = JobPreference(
        user_id=7,
        keywords=["Python", "FastAPI", "Backend"],
        locations=["Pakistan"],
        employment_types=["Full-time"],
        work_modes=["Remote"],
    )

    result = MatchingService.calculate_match_score(nurse_job, dev_preference)

    # Invariant: Must NOT receive 55% or any strong score
    assert result.total_score <= 15
    # Must NOT award location match for Davao vs Pakistan
    assert not any(r.category == "Location" for r in result.reasons)
    # Role relevance gate must be triggered
    assert any(r.category == "Role Relevance" for r in result.reasons)


def test_critical_relevant_job_scores_high():
    """Genuinely relevant job scores meaningfully higher (> 80%)."""
    backend_job = Job(
        id=400,
        source_id=2,
        external_id="ext-400",
        title="Python Backend Developer",
        company="CodeSphere",
        location="Pakistan",
        description="Design high-performance APIs using Python, FastAPI, and PostgreSQL.",
        url="https://example.com/jobs/backend",
        canonical_url="https://example.com/jobs/backend",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.REMOTE,
        dedupe_hash="hash-backend",
        raw_data={},
    )

    dev_preference = JobPreference(
        user_id=7,
        keywords=["Python", "FastAPI", "Backend"],
        locations=["Pakistan"],
        employment_types=["Full-time"],
        work_modes=["Remote"],
    )

    result = MatchingService.calculate_match_score(backend_job, dev_preference)
    assert result.total_score >= 85


def test_keyword_matching_avoids_false_positives():
    """Verify word boundary tokenization prevents false positives."""
    assert not match_keyword_token("Go", "Has good communication skills")
    assert not match_keyword_token("Go", "Experience with Google Cloud Platform")
    assert not match_keyword_token("C", "Customer support representative")
    assert not match_keyword_token("C", "Senior C++ Developer")
    assert not match_keyword_token("C", "Senior C# Developer")
    assert not match_keyword_token("Java", "Senior JavaScript & TypeScript Developer")
    assert not match_keyword_token("R", "Remote work environment")


def test_keyword_matching_preserves_technical_symbols():
    """Verify legitimate technical keywords with punctuation/symbols match properly."""
    assert match_keyword_token("C++", "Senior C++ Systems Engineer")
    assert match_keyword_token("C#", "C# .NET Backend Developer")
    assert match_keyword_token(".NET", "C# .NET Developer")
    assert match_keyword_token("Node.js", "Fullstack Node.js Developer")
    assert match_keyword_token("Next.js", "Frontend Next.js Architect")
    assert match_keyword_token("React Native", "React Native Mobile Engineer")
    assert match_keyword_token("React", "React and Next.js Developer")
    assert match_keyword_token("FastAPI", "Python FastAPI microservices")
    assert match_keyword_token("PostgreSQL", "Relational database with PostgreSQL")
    assert match_keyword_token("Go", "Senior Go Software Engineer")
    assert match_keyword_token("Python", "Python Backend Specialist")
