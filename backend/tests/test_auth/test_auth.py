import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    response = await client.post("/api/v1/auth/signup", json={
        "email": "newuser@example.com",
        "password": "SecureP@ss123",
        "full_name": "New User",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "newuser@example.com"
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    await client.post("/api/v1/auth/signup", json={
        "email": "dup@example.com",
        "password": "SecureP@ss123",
        "full_name": "Dup User",
    })
    response = await client.post("/api/v1/auth/signup", json={
        "email": "dup@example.com",
        "password": "SecureP@ss123",
        "full_name": "Dup User",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user):
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "TestP@ss1234",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == test_user.email
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "WrongPassword123!",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user):
    login_res = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "TestP@ss1234",
    })
    refresh_token = login_res.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_me_endpoint(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_endpoint_blocked(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/admin/users", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_endpoint_allowed(client: AsyncClient, admin_headers):
    response = await client.get("/api/v1/admin/users", headers=admin_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_signup_weak_password(client: AsyncClient):
    response = await client.post("/api/v1/auth/signup", json={
        "email": "weak@example.com",
        "password": "short",
        "full_name": "Weak Password",
    })
    assert response.status_code == 422
