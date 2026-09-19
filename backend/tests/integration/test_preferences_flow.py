import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_new_user_empty_preferences_flow(client: AsyncClient):
    """Verify that a brand new user receives clean empty preferences

    with is_configured == False and no fabricated match scores.
    """
    email = "cleanuser@example.com"
    reg_payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Clean User",
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch preferences - must be completely empty and unconfigured
    pref_res = await client.get("/api/v1/preferences", headers=headers)
    assert pref_res.status_code == 200
    pref_data = pref_res.json()
    assert pref_data["keywords"] == []
    assert pref_data["locations"] == []
    assert pref_data["employment_types"] == []
    assert pref_data["work_modes"] == []
    assert pref_data["min_salary"] is None
    assert pref_data["max_salary"] is None
    assert pref_data["is_configured"] is False

    # 2. Fetch notification settings - must be disabled by default
    notif_res = await client.get("/api/v1/preferences/notifications", headers=headers)
    assert notif_res.status_code == 200
    assert notif_res.json()["email_notifications"] is False

    # 3. Fetch jobs - match_score must be None for unconfigured preferences
    jobs_res = await client.get("/api/v1/jobs?page=1&page_size=10", headers=headers)
    assert jobs_res.status_code == 200
    for job in jobs_res.json()["items"]:
        assert job["match_score"] is None
        assert job["match_reasons"] == []

    # 4. User configures preferences
    update_res = await client.put(
        "/api/v1/preferences",
        headers=headers,
        json={
            "keywords": ["Python", "FastAPI"],
            "locations": ["Remote"],
            "work_modes": ["Remote"],
            "employment_types": ["Full-time"],
        },
    )
    assert update_res.status_code == 200
    assert update_res.json()["is_configured"] is True

    # 5. Fetch jobs again - match_score must now be computed
    jobs_after = await client.get("/api/v1/jobs?page=1&page_size=10", headers=headers)
    assert jobs_after.status_code == 200
    items = jobs_after.json()["items"]
    if items:
        # At least one job should have a computed integer match_score
        assert any(item["match_score"] is not None for item in items)
