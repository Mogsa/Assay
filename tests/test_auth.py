import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_creates_human_agent(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "morgan@example.com",
            "password": "securepass123",
            "display_name": "Morgan",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["agent_id"]
    assert data["display_name"] == "Morgan"
    assert "session" in resp.cookies


@pytest.mark.asyncio
async def test_signup_duplicate_email_returns_409(client: AsyncClient):
    payload = {
        "email": "dupe@example.com",
        "password": "securepass123",
        "display_name": "First",
    }
    resp1 = await client.post("/api/v1/auth/signup", json=payload)
    assert resp1.status_code == 201

    payload["display_name"] = "Second"
    resp2 = await client.post("/api/v1/auth/signup", json=payload)
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_signup_short_password_returns_422(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "short@example.com",
            "password": "abc",
            "display_name": "Short",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_returns_session_cookie(client: AsyncClient):
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "login@example.com", "password": "securepass123", "display_name": "Login"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    assert resp.status_code == 200
    assert "session" in resp.cookies
    assert resp.json()["display_name"] == "Login"


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client: AsyncClient):
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "wrong@example.com", "password": "securepass123", "display_name": "Wrong"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "badpassword1"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_email_returns_401(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "irrelevant1"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_clears_session(client: AsyncClient):
    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "logout@example.com", "password": "securepass123", "display_name": "Logout"},
    )
    session_cookie = signup_resp.cookies.get("session")

    resp = await client.post(
        "/api/v1/auth/logout",
        cookies={"session": session_cookie},
    )
    assert resp.status_code == 200

    # Old session should be invalid
    me_resp = await client.get(
        "/api/v1/agents/me",
        cookies={"session": session_cookie},
    )
    assert me_resp.status_code == 401


@pytest.mark.asyncio
async def test_session_cookie_authenticates_to_agents_me(client: AsyncClient):
    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "cookie@example.com", "password": "securepass123", "display_name": "Cookie"},
    )
    session_cookie = signup_resp.cookies.get("session")

    me_resp = await client.get(
        "/api/v1/agents/me",
        cookies={"session": session_cookie},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["display_name"] == "Cookie"
    assert me_resp.json()["agent_type"] == "human"


@pytest.mark.asyncio
async def test_logout_without_session_returns_401(client: AsyncClient):
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 401
