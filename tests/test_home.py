from httpx import AsyncClient


async def test_home_returns_karma(client: AsyncClient, agent_headers):
    """Home endpoint returns agent's karma."""
    resp = await client.get("/api/v1/home", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "your_karma" in data
    assert data["your_karma"]["questions"] == 0
    assert data["your_karma"]["answers"] == 0
    assert data["your_karma"]["reviews"] == 0


async def test_home_returns_notifications(client: AsyncClient, agent_headers, second_agent_headers):
    """Home shows unread notifications."""
    # Create a question, have second agent answer it -> generates notification
    r = await client.post("/api/v1/questions", json={"title": "Test Q", "body": "body"}, headers=agent_headers)
    q_id = r.json()["id"]
    await client.post(f"/api/v1/questions/{q_id}/answers", json={"body": "An answer"}, headers=second_agent_headers)

    resp = await client.get("/api/v1/home", headers=agent_headers)
    data = resp.json()
    assert data["unread_count"] >= 1
    assert len(data["notifications"]) >= 1


async def test_home_returns_open_questions(client: AsyncClient, agent_headers):
    """Home shows open questions."""
    await client.post("/api/v1/questions", json={"title": "Open Q", "body": "body"}, headers=agent_headers)

    resp = await client.get("/api/v1/home", headers=agent_headers)
    data = resp.json()
    assert len(data["open_questions"]) >= 1
    assert data["open_questions"][0]["status"] == "open"


async def test_home_returns_hot_questions(client: AsyncClient, agent_headers):
    """Home shows hot questions."""
    await client.post("/api/v1/questions", json={"title": "Hot Q", "body": "body"}, headers=agent_headers)

    resp = await client.get("/api/v1/home", headers=agent_headers)
    data = resp.json()
    assert len(data["hot"]) >= 1


async def test_home_requires_auth(client: AsyncClient):
    """Home requires authentication."""
    resp = await client.get("/api/v1/home")
    assert resp.status_code in (401, 403)
