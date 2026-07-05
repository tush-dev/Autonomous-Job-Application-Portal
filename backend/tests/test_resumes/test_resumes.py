import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_resume(client: AsyncClient, auth_headers):
    files = {"file": ("resume.pdf", b"%PDF-1.4 test content", "application/pdf")}
    response = await client.post("/api/v1/resumes/upload", files=files, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["file_type"] == "pdf"


@pytest.mark.asyncio
async def test_list_resumes(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/resumes", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_resume_analysis(client: AsyncClient, auth_headers):
    upload = await client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.pdf", b"%PDF-1.4 test", "application/pdf")},
        headers=auth_headers,
    )
    resume_id = upload.json()["id"]

    response = await client.get(f"/api/v1/resumes/{resume_id}/analysis", headers=auth_headers)
    assert response.status_code == 200
    assert "skills" in response.json()
