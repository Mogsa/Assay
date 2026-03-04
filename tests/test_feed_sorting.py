import pytest
from httpx import AsyncClient


async def test_feed_default_is_new(client: AsyncClient, agent_headers):
    """Default sort is newest first (ordered by created_at desc)."""
    for i in range(3):
        await client.post(
            "/api/v1/questions",
            json={"title": f"Q{i}", "body": f"body {i}"},
            headers=agent_headers,
        )

    resp = await client.get("/api/v1/questions", headers=agent_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 3
    # Verify descending order by created_at
    timestamps = [item["created_at"] for item in items]
    assert timestamps == sorted(timestamps, reverse=True)


async def test_feed_sort_new(client: AsyncClient, agent_headers):
    """Explicit sort=new returns results ordered by created_at desc."""
    for i in range(3):
        await client.post(
            "/api/v1/questions",
            json={"title": f"SortNew{i}", "body": "body"},
            headers=agent_headers,
        )

    resp = await client.get(
        "/api/v1/questions", params={"sort": "new"}, headers=agent_headers
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 3
    # Verify descending order by created_at
    timestamps = [item["created_at"] for item in items]
    assert timestamps == sorted(timestamps, reverse=True)


async def test_feed_sort_hot(client: AsyncClient, agent_headers, second_agent_headers):
    """Sort=hot returns results (hot_score function works)."""
    await client.post(
        "/api/v1/questions",
        json={"title": "Cold Q", "body": "no votes"},
        headers=agent_headers,
    )
    resp2 = await client.post(
        "/api/v1/questions",
        json={"title": "Hot Q", "body": "many votes"},
        headers=agent_headers,
    )
    hot_id = resp2.json()["id"]

    # Upvote the hot question
    await client.post(
        f"/api/v1/questions/{hot_id}/vote",
        json={"value": 1},
        headers=second_agent_headers,
    )

    resp = await client.get(
        "/api/v1/questions", params={"sort": "hot"}, headers=agent_headers
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 2
    # Both questions present; hot_score endpoint works without error
    titles = {item["title"] for item in items}
    assert titles == {"Cold Q", "Hot Q"}


async def test_feed_sort_open(client: AsyncClient, agent_headers):
    """Sort=open only returns open questions."""
    await client.post(
        "/api/v1/questions",
        json={"title": "Open Q", "body": "body"},
        headers=agent_headers,
    )

    resp = await client.get(
        "/api/v1/questions", params={"sort": "open"}, headers=agent_headers
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["status"] == "open"


async def test_feed_invalid_sort(client: AsyncClient, agent_headers):
    """Invalid sort value returns 422."""
    resp = await client.get(
        "/api/v1/questions", params={"sort": "invalid"}, headers=agent_headers
    )
    assert resp.status_code == 422
