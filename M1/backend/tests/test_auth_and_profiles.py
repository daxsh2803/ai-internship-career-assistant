
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_registration_and_login_flow(async_client: AsyncClient):
    register_payload = {
        "email": "jane.doe@stanford.edu",
        "password": "Password123!",
        "full_name": "Jane Doe",
        "role": "STUDENT",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "jane.doe@stanford.edu"
    assert reg_data["user"]["full_name"] == "Jane Doe"
    assert reg_data["user"]["role"] == "STUDENT"

    token = reg_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dup_res = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert dup_res.status_code == 409

    login_payload = {
        "email": "jane.doe@stanford.edu",
        "password": "Password123!",
    }
    login_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "jane.doe@stanford.edu"

@pytest.mark.asyncio
async def test_candidate_profile_creation_and_retrieval(async_client: AsyncClient):
    reg_payload = {
        "email": "alex.student@mit.edu",
        "password": "SecurePassword123!",
        "full_name": "Alex Student",
        "role": "STUDENT",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_payload = {
        "university_name": "Massachusetts Institute of Technology",
        "degree_major": "Computer Science and AI",
        "gpa": 3.92,
        "graduation_term": "Spring",
        "graduation_year": 2026,
        "requires_sponsorship": False,
        "preferred_locations": ["San Francisco, CA", "Boston, MA", "Remote"],
    }
    create_res = await async_client.post("/api/v1/profiles", json=profile_payload, headers=headers)
    assert create_res.status_code == 201
    profile_data = create_res.json()
    assert profile_data["university_name"] == "Massachusetts Institute of Technology"
    assert profile_data["gpa"] == 3.92
    assert profile_data["graduation_year"] == 2026
    assert "Remote" in profile_data["preferred_locations"]

    get_res = await async_client.get("/api/v1/profiles/me", headers=headers)
    assert get_res.status_code == 200
    fetched_data = get_res.json()
    assert fetched_data["id"] == profile_data["id"]
    assert fetched_data["degree_major"] == "Computer Science and AI"
