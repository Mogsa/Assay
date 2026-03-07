import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_agents_mine_lists_created_agents(client: AsyncClient):
    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "multi@example.com", "password": "securepass123", "display_name": "Multi"},
    )
    cookie = signup_resp.cookies.get("session")

    for display_name, model_slug, runtime_kind in [
        ("Bot1", "openai/gpt-4o", "openai-api"),
        ("Bot2", "anthropic/claude-opus-4-6", "claude-cli"),
    ]:
        response = await client.post(
            "/api/v1/agents",
            cookies={"session": cookie},
            json={
                "display_name": display_name,
                "model_slug": model_slug,
                "runtime_kind": runtime_kind,
            },
        )
        assert response.status_code == 201

    resp = await client.get("/api/v1/agents/mine", cookies={"session": cookie})
    assert resp.status_code == 200
    names = [a["display_name"] for a in resp.json()["agents"]]
    assert "Bot1" in names
    assert "Bot2" in names


@pytest.mark.asyncio
async def test_agents_mine_rejects_bearer_auth(client: AsyncClient, agent_headers: dict):
    resp = await client.get("/api/v1/agents/mine", headers=agent_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_agents_mine_only_returns_owned_agents(client: AsyncClient):
    first_signup = await client.post(
        "/api/v1/auth/signup",
        json={"email": "first@example.com", "password": "securepass123", "display_name": "First"},
    )
    second_signup = await client.post(
        "/api/v1/auth/signup",
        json={"email": "second@example.com", "password": "securepass123", "display_name": "Second"},
    )
    first_cookie = first_signup.cookies.get("session")
    second_cookie = second_signup.cookies.get("session")

    await client.post(
        "/api/v1/agents",
        cookies={"session": first_cookie},
        json={
            "display_name": "FirstAgent",
            "model_slug": "openai/gpt-5",
            "runtime_kind": "codex-cli",
        },
    )
    await client.post(
        "/api/v1/agents",
        cookies={"session": second_cookie},
        json={
            "display_name": "SecondAgent",
            "model_slug": "openai/gpt-4o",
            "runtime_kind": "openai-api",
        },
    )

    mine = await client.get("/api/v1/agents/mine", cookies={"session": first_cookie})
    assert mine.status_code == 200
    names = [a["display_name"] for a in mine.json()["agents"]]
    assert names == ["FirstAgent"]
