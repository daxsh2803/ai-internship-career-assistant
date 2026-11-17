
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_job_creation_and_application_lifecycle(async_client: AsyncClient):
    reg_payload = {
        "email": "sarah.dev@berkeley.edu",
        "password": "Password123!",
        "full_name": "Sarah Developer",
        "role": "STUDENT",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_payload = {
        "university_name": "UC Berkeley",
        "degree_major": "EECS",
        "gpa": 3.85,
        "graduation_term": "Spring",
        "graduation_year": 2026,
        "requires_sponsorship": False,
        "preferred_locations": ["Remote", "San Francisco"],
    }
    await async_client.post("/api/v1/profiles", json=profile_payload, headers=headers)

    job_payload = {
        "title": "Backend Engineering Intern",
        "company_name": "CloudScale Systems",
        "location": "San Francisco, CA",
        "is_remote": True,
        "raw_description": "We are seeking a Backend Engineering Intern proficient in Python, FastAPI, and PostgreSQL to build scalable microservices.",
        "cleaned_markdown": "### Requirements:\n- Python 3.11+\n- FastAPI / Asyncio\n- PostgreSQL & pgvector",
        "min_gpa": 3.0,
        "required_graduation_years": [2025, 2026],
        "visa_sponsorship_available": True,
        "monthly_stipend_cents": 600000,
        "requirements": [
            {
                "requirement_type": "HARD_SKILL",
                "description": "Proficiency in Python and asynchronous API development.",
                "is_mandatory": True,
            },
            {
                "requirement_type": "HARD_SKILL",
                "description": "Experience with relational databases and SQL queries.",
                "is_mandatory": True,
            },
        ],
    }
    job_res = await async_client.post("/api/v1/jobs", json=job_payload, headers=headers)
    assert job_res.status_code == 201
    job_data = job_res.json()
    job_id = job_data["id"]
    assert job_data["title"] == "Backend Engineering Intern"
    assert len(job_data["requirements"]) == 2

    list_res = await async_client.get("/api/v1/jobs?is_remote=true")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(j["id"] == job_id for j in list_data["items"])

    app_payload = {
        "job_id": job_id,
        "cover_letter_markdown": "I am thrilled to apply for the Backend Engineering Intern position.",
    }
    app_res = await async_client.post("/api/v1/applications", json=app_payload, headers=headers)
    assert app_res.status_code == 201
    app_data = app_res.json()
    app_id = app_data["id"]
    assert app_data["current_stage"] == "WISHLIST"
    assert app_data["job_title"] == "Backend Engineering Intern"
    assert len(app_data["stage_history"]) == 1

    dup_app = await async_client.post("/api/v1/applications", json=app_payload, headers=headers)
    assert dup_app.status_code == 409

    stage_update = {
        "new_stage": "APPLIED",
        "notes": "Submitted official application on portal.",
    }
    patch_res = await async_client.patch(
        f"/api/v1/applications/{app_id}/stage", json=stage_update, headers=headers
    )
    assert patch_res.status_code == 200
    updated_app = patch_res.json()
    assert updated_app["current_stage"] == "APPLIED"
    assert len(updated_app["stage_history"]) == 2
    assert updated_app["stage_history"][-1]["new_stage"] == "APPLIED"

    kanban_res = await async_client.get("/api/v1/applications/kanban", headers=headers)
    assert kanban_res.status_code == 200
    board = kanban_res.json()
    assert len(board["applied"]) == 1
    assert board["applied"][0]["id"] == app_id
    assert len(board["wishlist"]) == 0
