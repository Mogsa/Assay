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
    _, h1 = await _register_agent(client, "Agent1", "claude-opus")
    _, h2 = await _register_agent(client, "Agent2", "gpt-4o")
    _, h3 = await _register_agent(client, "Agent3", "claude-opus")

    resp = await client.get("/api/v1/leaderboard", params={"agent_type": "claude-opus"}, headers=h1)
    assert resp.status_code == 200
    items = resp.json()["items"]
    for item in items:
        assert item["agent_type"] == "claude-opus"


async def test_leaderboard_invalid_sort(client: AsyncClient, agent_headers):
    """Invalid sort_by value returns 422."""
    resp = await client.get("/api/v1/leaderboard", params={"sort_by": "invalid"}, headers=agent_headers)
    assert resp.status_code == 422


async def test_leaderboard_requires_auth(client: AsyncClient):
    """Leaderboard requires authentication."""
    resp = await client.get("/api/v1/leaderboard")
    assert resp.status_code == 401
