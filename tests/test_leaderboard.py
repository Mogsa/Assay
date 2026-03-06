import pytest
from httpx import AsyncClient


async def _register_agent(client: AsyncClient, name: str, agent_type: str) -> tuple[str, dict]:
    """Register an agent and return (agent_id, headers)."""
    resp = await client.post(
        "/api/v1/agents/register",
        json={"display_name": name, "agent_type": agent_type},
    )
    data = resp.json()
    return data["agent_id"], {"Authorization": f"Bearer {data['api_key']}"}


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
    """Can filter leaderboard by agent_type."""
    signup = await client.post(
        "/api/v1/auth/signup",
        json={"email": "lb-owner@example.com", "password": "securepass123", "display_name": "Owner"},
    )
    cookie = signup.cookies.get("session")

    r1 = await client.post("/api/v1/agents/register", json={"display_name": "Agent1", "agent_type": "claude-opus"})
    r2 = await client.post("/api/v1/agents/register", json={"display_name": "Agent2", "agent_type": "gpt-4o"})
    r3 = await client.post("/api/v1/agents/register", json={"display_name": "Agent3", "agent_type": "claude-opus"})
    await client.post(
        f"/api/v1/agents/claim/{r1.json()['claim_url'].rstrip('/').split('/')[-1]}",
        cookies={"session": cookie},
    )
    await client.post(
        f"/api/v1/agents/claim/{r2.json()['claim_url'].rstrip('/').split('/')[-1]}",
        cookies={"session": cookie},
    )
    await client.post(
        f"/api/v1/agents/claim/{r3.json()['claim_url'].rstrip('/').split('/')[-1]}",
        cookies={"session": cookie},
    )

    resp = await client.get("/api/v1/leaderboard", params={"agent_type": "claude-opus"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert items
    for item in items:
        assert item["agent_type"] == "claude-opus"


async def test_leaderboard_invalid_sort(client: AsyncClient, agent_headers):
    """Invalid sort_by value returns 422."""
    resp = await client.get("/api/v1/leaderboard", params={"sort_by": "invalid"}, headers=agent_headers)
    assert resp.status_code == 422


async def test_leaderboard_is_public(client: AsyncClient):
    """Leaderboard is publicly readable."""
    resp = await client.get("/api/v1/leaderboard")
    assert resp.status_code == 200


async def test_leaderboard_agent_types_view(client: AsyncClient, human_session_cookie: str):
    create_a = await client.post(
        "/api/v1/agents",
        json={"display_name": "Claude A", "agent_type": "claude-opus"},
        cookies={"session": human_session_cookie},
    )
    assert create_a.status_code == 201
    create_b = await client.post(
        "/api/v1/agents",
        json={"display_name": "Claude B", "agent_type": "claude-opus"},
        cookies={"session": human_session_cookie},
    )
    assert create_b.status_code == 201

    h_a = {"Authorization": f"Bearer {create_a.json()['api_key']}"}
    h_b = {"Authorization": f"Bearer {create_b.json()['api_key']}"}

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
    assert any(item["agent_type"] == "claude-opus" for item in items)
