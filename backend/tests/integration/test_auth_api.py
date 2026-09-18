import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_registration_and_login_flow(client: AsyncClient):
    # 1. Register user
    reg_payload = {
        "email": "testuser@example.com",
        "password": "Password123!",
        "full_name": "Test User",
    }
    response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"

    # 2. Login user
    login_payload = {
        "email": "testuser@example.com",
        "password": "Password123!",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data

    # 3. Access /me endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "testuser@example.com"
