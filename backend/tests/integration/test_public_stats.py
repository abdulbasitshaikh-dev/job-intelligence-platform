import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_public_stats_endpoint(client: AsyncClient):
    # Test top-level shortcut route /api/v1/stats
    response = await client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "active_jobs" in data
    assert "total_jobs" in data
    assert "configured_sources" in data
    assert "healthy_sources" in data

    # Test /api/v1/jobs/stats
    job_stats_res = await client.get("/api/v1/jobs/stats")
    assert job_stats_res.status_code == 200
    assert job_stats_res.json()["active_jobs"] == data["active_jobs"]


@pytest.mark.asyncio
async def test_public_sources_endpoint(client: AsyncClient):
    response = await client.get("/api/v1/sources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_jobs_sync_unauthorized(client: AsyncClient):
    # POST /api/v1/jobs/sync should reject anonymous calls
    response = await client.post("/api/v1/jobs/sync")
    assert response.status_code == 401
