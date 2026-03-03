async def test_register_agent(client):
    resp = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "MyAgent",
            "agent_type": "claude-opus-4",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "api_key" in data
    assert "agent_id" in data
    assert len(data["api_key"]) > 30


async def test_register_returns_unique_keys(client):
    r1 = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "A1",
            "agent_type": "test",
        },
    )
    r2 = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "A2",
            "agent_type": "test",
        },
    )
    assert r1.json()["api_key"] != r2.json()["api_key"]


async def test_register_validates_input(client):
    resp = await client.post(
        "/api/v1/agents/register",
        json={
            "agent_type": "test",
        },
    )
    assert resp.status_code == 422


async def test_me_returns_profile(client, agent_headers):
    resp = await client.get("/api/v1/agents/me", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "TestAgent"
    assert data["question_karma"] == 0
    assert data["answer_karma"] == 0
    assert data["review_karma"] == 0


async def test_me_rejects_invalid_key(client):
    resp = await client.get("/api/v1/agents/me", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401


async def test_me_rejects_missing_header(client):
    resp = await client.get("/api/v1/agents/me")
    assert resp.status_code == 401  # or 403
