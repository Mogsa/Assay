async def test_catalog_endpoints_list_seeded_models_and_runtimes(client):
    models = await client.get("/api/v1/catalog/models")
    assert models.status_code == 200
    model_slugs = {item["slug"] for item in models.json()}
    assert "anthropic/claude-opus-4" in model_slugs
    assert "openai/gpt-5" in model_slugs

    runtimes = await client.get("/api/v1/catalog/runtimes")
    assert runtimes.status_code == 200
    runtime_slugs = {item["slug"] for item in runtimes.json()}
    assert "claude-cli" in runtime_slugs
    assert "codex-cli" in runtime_slugs


async def test_device_start_requires_ack_for_warning_model_runtime(client):
    response = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "Warning Agent",
            "model_slug": "anthropic/claude-opus-4",
            "runtime_kind": "claude-cli",
        },
    )
    assert response.status_code == 400
    assert "Anthropic" in response.json()["detail"]


async def test_device_flow_approval_poll_and_refresh(client):
    start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "Device Agent",
            "model_slug": "anthropic/claude-opus-4",
            "runtime_kind": "claude-cli",
            "provider_terms_acknowledged": True,
        },
    )
    assert start.status_code == 201
    payload = start.json()
    assert payload["support_level"] == "warning"

    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "device-owner@example.com",
            "password": "securepass123",
            "display_name": "Device Owner",
        },
    )
    session_cookie = signup.cookies.get("session")
    approve = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": session_cookie},
        json={"user_code": payload["user_code"]},
    )
    assert approve.status_code == 200

    poll = await client.post(
        "/api/v1/cli/device/poll",
        json={"device_code": payload["device_code"]},
    )
    assert poll.status_code == 200
    tokens = poll.json()
    assert tokens["status"] == "approved"
    assert tokens["model_slug"] == "anthropic/claude-opus-4"
    assert tokens["runtime_kind"] == "claude-cli"

    me = await client.get(
        "/api/v1/agents/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["model_slug"] == "anthropic/claude-opus-4"

    refreshed = await client.post(
        "/api/v1/cli/token/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"] != tokens["access_token"]


async def test_device_flow_denial_blocks_poll(client, human_session_cookie: str):
    start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "Denied Agent",
            "model_slug": "openai/gpt-5",
            "runtime_kind": "codex-cli",
        },
    )
    assert start.status_code == 201
    payload = start.json()

    deny = await client.post(
        "/api/v1/cli/device/deny",
        cookies={"session": human_session_cookie},
        json={"user_code": payload["user_code"]},
    )
    assert deny.status_code == 200

    poll = await client.post(
        "/api/v1/cli/device/poll",
        json={"device_code": payload["device_code"]},
    )
    assert poll.status_code == 403


async def test_device_flow_custom_model_creates_noncanonical_profile(client, human_session_cookie: str):
    start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "Local Qwen",
            "custom_model": {"provider": "ollama", "model_name": "qwen-local"},
            "runtime_kind": "local-command",
            "provider_terms_acknowledged": True,
        },
    )
    assert start.status_code == 201
    payload = start.json()
    assert payload["support_level"] == "warning"

    approve = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": human_session_cookie},
        json={"user_code": payload["user_code"]},
    )
    assert approve.status_code == 200

    poll = await client.post(
        "/api/v1/cli/device/poll",
        json={"device_code": payload["device_code"]},
    )
    tokens = poll.json()

    me = await client.get(
        "/api/v1/agents/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["model_slug"].startswith("custom/ollama/")
    assert me.json()["agent_type_average"] is None


async def test_owner_can_rotate_agent_api_key(client, human_session_cookie: str):
    start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "Rotatable",
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
    created = poll.json()

    rotated = await client.post(
        f"/api/v1/agents/{created['agent_id']}/api-key",
        cookies={"session": human_session_cookie},
    )
    assert rotated.status_code == 200
    new_key = rotated.json()["api_key"]

    new_me = await client.get(
        "/api/v1/agents/me",
        headers={"Authorization": f"Bearer {new_key}"},
    )
    assert new_me.status_code == 200


async def test_skill_version_endpoint(client):
    version = await client.get("/api/v1/skill/version")
    assert version.status_code == 200
    assert len(version.json()["version"]) == 12
