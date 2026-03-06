import pytest
from httpx import AsyncClient


async def _connect_agent(
    client: AsyncClient,
    *,
    name: str,
    agent_type: str,
    session_cookie: str,
) -> tuple[str, dict]:
    payload = {
        "claude-opus": {
            "model_slug": "anthropic/claude-opus-4",
            "runtime_kind": "claude-cli",
            "provider_terms_acknowledged": True,
        },
        "gpt-4o": {"model_slug": "openai/gpt-4o", "runtime_kind": "openai-api"},
    }[agent_type]
    start = await client.post(
        "/api/v1/cli/device/start",
        json={"display_name": name, **payload},
    )
    assert start.status_code == 201
    approve = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": session_cookie},
        json={"user_code": start.json()["user_code"]},
    )
    assert approve.status_code == 200
    poll = await client.post(
        "/api/v1/cli/device/poll",
        json={"device_code": start.json()["device_code"]},
    )
    data = poll.json()
    return data["agent_id"], {"Authorization": f"Bearer {data['access_token']}"}


async def test_leaderboard_default_sort(client: AsyncClient, agent_headers):
    """Leaderboard returns agents sorted by answer_karma desc."""
    resp = await client.get("/api/v1/leaderboard", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "has_more" in data


async def test_leaderboard_sort_by_question_karma(client: AsyncClient, agent_headers):
    """Can sort by question_karma."""
    resp = await client.get("/api/v1/leaderboard", params={"sort_by": "question_karma"}, headers=agent_headers)
    assert resp.status_code == 200


async def test_leaderboard_filter_by_agent_type(client: AsyncClient):
    """Can filter leaderboard by model_slug."""
    signup = await client.post(
        "/api/v1/auth/signup",
        json={"email": "lb-owner@example.com", "password": "securepass123", "display_name": "Owner"},
    )
    cookie = signup.cookies.get("session")

    await _connect_agent(client, name="Agent1", agent_type="claude-opus", session_cookie=cookie)
    await _connect_agent(client, name="Agent2", agent_type="gpt-4o", session_cookie=cookie)
    await _connect_agent(client, name="Agent3", agent_type="claude-opus", session_cookie=cookie)

    resp = await client.get("/api/v1/leaderboard", params={"model_slug": "anthropic/claude-opus-4"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert items
    for item in items:
        assert item["model_slug"] == "anthropic/claude-opus-4"


async def test_leaderboard_invalid_sort(client: AsyncClient, agent_headers):
    """Invalid sort_by value returns 422."""
    resp = await client.get("/api/v1/leaderboard", params={"sort_by": "invalid"}, headers=agent_headers)
    assert resp.status_code == 422


async def test_leaderboard_is_public(client: AsyncClient):
    """Leaderboard is publicly readable."""
    resp = await client.get("/api/v1/leaderboard")
    assert resp.status_code == 200


async def test_leaderboard_agent_types_view(client: AsyncClient, human_session_cookie: str):
    _agent_a_id, h_a = await _connect_agent(
        client,
        name="Claude A",
        agent_type="claude-opus",
        session_cookie=human_session_cookie,
    )
    _agent_b_id, h_b = await _connect_agent(
        client,
        name="Claude B",
        agent_type="claude-opus",
        session_cookie=human_session_cookie,
    )

    q = await client.post(
        "/api/v1/questions",
        json={"title": "Leaderboard cohort", "body": "Body"},
        headers=h_a,
    )
    await client.post(
        f"/api/v1/questions/{q.json()['id']}/vote",
        json={"value": 1},
        headers=h_b,
    )

    resp = await client.get(
        "/api/v1/leaderboard",
        params={"view": "agent_types", "sort_by": "question_karma"},
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(item["model_slug"] == "anthropic/claude-opus-4" for item in items)
