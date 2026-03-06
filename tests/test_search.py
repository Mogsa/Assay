import pytest
from httpx import AsyncClient


async def test_search_by_title(client: AsyncClient, agent_headers):
    """Search finds questions by title keyword."""
    await client.post(
        "/api/v1/questions",
        json={"title": "Python asyncio tutorial", "body": "How does asyncio work?"},
        headers=agent_headers,
    )
    await client.post(
        "/api/v1/questions",
        json={"title": "JavaScript promises", "body": "Understanding promises"},
        headers=agent_headers,
    )

    resp = await client.get("/api/v1/search", params={"q": "asyncio"}, headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert "asyncio" in data["items"][0]["title"].lower()


async def test_search_by_body(client: AsyncClient, agent_headers):
    """Search finds questions by body content."""
    await client.post(
        "/api/v1/questions",
        json={"title": "Help needed", "body": "I need help with PostgreSQL indexing strategies"},
        headers=agent_headers,
    )

    resp = await client.get("/api/v1/search", params={"q": "PostgreSQL indexing"}, headers=agent_headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


async def test_search_no_results(client: AsyncClient, agent_headers):
    """Search returns empty when no match."""
    await client.post(
        "/api/v1/questions",
        json={"title": "Python tutorial", "body": "Learn Python basics"},
        headers=agent_headers,
    )

    resp = await client.get("/api/v1/search", params={"q": "kubernetes"}, headers=agent_headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 0


async def test_search_is_public(client: AsyncClient):
    """Search is publicly readable."""
    resp = await client.get("/api/v1/search", params={"q": "test"})
    assert resp.status_code == 200


async def test_search_requires_query(client: AsyncClient, agent_headers):
    """Search requires a query parameter."""
    resp = await client.get("/api/v1/search", headers=agent_headers)
    assert resp.status_code == 422


async def test_search_items_include_viewer_vote(client: AsyncClient, agent_headers, second_agent_headers):
    create = await client.post(
        "/api/v1/questions",
        json={"title": "Search vote state", "body": "Body"},
        headers=agent_headers,
    )
    qid = create.json()["id"]
    await client.post(
        f"/api/v1/questions/{qid}/vote",
        json={"value": 1},
        headers=second_agent_headers,
    )

    resp = await client.get("/api/v1/search", params={"q": "Search vote state"}, headers=second_agent_headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1
    assert resp.json()["items"][0]["viewer_vote"] == 1
