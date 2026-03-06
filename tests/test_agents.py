async def test_device_login_creates_agent_and_returns_tokens(client, human_session_cookie: str):
    start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "MyAgent",
            "model_slug": "anthropic/claude-opus-4",
            "runtime_kind": "claude-cli",
            "provider_terms_acknowledged": True,
        },
    )
    assert start.status_code == 201

    approve = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": human_session_cookie},
        json={"user_code": start.json()["user_code"]},
    )
    assert approve.status_code == 200

    poll = await client.post(
        "/api/v1/cli/device/poll",
        json={"device_code": start.json()["device_code"]},
    )
    assert poll.status_code == 200
    tokens = poll.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens


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
    assert resp.status_code == 401


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


async def test_owner_can_revoke_agent_tokens(client, human_session_cookie: str):
    start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "Revocable",
            "model_slug": "openai/gpt-4o",
            "runtime_kind": "openai-api",
        },
    )
    approve = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": human_session_cookie},
        json={"user_code": start.json()["user_code"]},
    )
    assert approve.status_code == 200
    poll = await client.post(
        "/api/v1/cli/device/poll",
        json={"device_code": start.json()["device_code"]},
    )
    tokens = poll.json()

    revoked = await client.post(
        f"/api/v1/agents/{tokens['agent_id']}/tokens/revoke-all",
        cookies={"session": human_session_cookie},
    )
    assert revoked.status_code == 200
    assert revoked.json()["revoked_count"] >= 2

    me = await client.get(
        "/api/v1/agents/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 401
