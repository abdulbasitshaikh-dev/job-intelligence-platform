import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.source import Source, SourceType


@pytest.mark.asyncio
async def test_search_ranking_relevance(db_session: AsyncSession, client):
    # Setup a Source
    source = Source(
        name="Test Feed",
        base_url="https://test.example.com",
        source_type=SourceType.API,
        scraper_type="remote_ok",
        enabled=True,
    )
    db_session.add(source)
    await db_session.flush()

    # Job A: Query "Kubernetes" only in description
    job_desc = Job(
        source_id=source.id,
        external_id="ext-desc",
        title="DevOps Engineer",
        company="Alpha Corp",
        location="Remote",
        description="Looking for an engineer experienced with Docker and Kubernetes cluster management.",
        url="https://example.com/job/desc",
        canonical_url="https://example.com/job/desc",
        dedupe_hash="hash-desc-1",
        is_active=True,
    )

    # Job B: Query "Kubernetes" in Title
    job_title = Job(
        source_id=source.id,
        external_id="ext-title",
        title="Kubernetes Specialist",
        company="Beta Corp",
        location="Remote",
        description="Manage our infrastructure and cloud operations.",
        url="https://example.com/job/title",
        canonical_url="https://example.com/job/title",
        dedupe_hash="hash-title-2",
        is_active=True,
    )

    db_session.add_all([job_desc, job_title])
    await db_session.commit()

    # Query search API for "Kubernetes"
    response = await client.get("/api/v1/jobs/search?q=Kubernetes")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 2
    # The title match must rank first ahead of description-only match
    first_job = data["items"][0]
    assert first_job["title"] == "Kubernetes Specialist"
