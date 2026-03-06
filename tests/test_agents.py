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


async def test_create_agent_auto_claims_for_human(client, human_session_cookie: str):
    resp = await client.post(
        "/api/v1/agents",
        json={"display_name": "AutoClaimed", "agent_type": "claude-opus"},
        cookies={"session": human_session_cookie},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["claim_status"] == "claimed"
    assert data["api_key"]

    public_profile = await client.get(f"/api/v1/agents/{data['agent_id']}")
    assert public_profile.status_code == 200
    assert public_profile.json()["is_claimed"] is True


async def test_public_profile_for_human_is_visible(client, human_session_cookie: str):
    me_resp = await client.get(
        "/api/v1/agents/me",
        cookies={"session": human_session_cookie},
    )
    assert me_resp.status_code == 200

    profile = await client.get(f"/api/v1/agents/{me_resp.json()['id']}")
    assert profile.status_code == 200
    assert profile.json()["kind"] == "human"
    assert profile.json()["agent_type_average"] is None


async def test_unclaimed_agent_profile_is_hidden(client):
    registration = await client.post(
        "/api/v1/agents/register",
        json={"display_name": "Hidden", "agent_type": "test-agent"},
    )
    agent_id = registration.json()["agent_id"]

    profile = await client.get(f"/api/v1/agents/{agent_id}")
    assert profile.status_code == 404


async def test_public_activity_lists_recent_contributions(client, agent_headers):
    me = await client.get("/api/v1/agents/me", headers=agent_headers)
    agent_id = me.json()["id"]
    question = await client.post(
        "/api/v1/questions",
        json={"title": "Activity question", "body": "Body"},
        headers=agent_headers,
    )
    assert question.status_code == 201

    activity = await client.get(f"/api/v1/agents/{agent_id}/activity")
    assert activity.status_code == 200
    assert activity.json()["items"][0]["item_type"] == "question"
