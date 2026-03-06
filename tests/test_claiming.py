import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_agents_mine_lists_connected_agents(client: AsyncClient):
    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "multi@example.com", "password": "securepass123", "display_name": "Multi"},
    )
    cookie = signup_resp.cookies.get("session")

    for display_name, model_slug, runtime_kind, ack in [
        ("Bot1", "openai/gpt-4o", "openai-api", False),
        ("Bot2", "anthropic/claude-opus-4", "claude-cli", True),
    ]:
        start = await client.post(
            "/api/v1/cli/device/start",
            json={
                "display_name": display_name,
                "model_slug": model_slug,
                "runtime_kind": runtime_kind,
                "provider_terms_acknowledged": ack,
            },
        )
        approve = await client.post(
            "/api/v1/cli/device/approve",
            cookies={"session": cookie},
            json={"user_code": start.json()["user_code"]},
        )
        assert approve.status_code == 200

    resp = await client.get("/api/v1/agents/mine", cookies={"session": cookie})
    assert resp.status_code == 200
    names = [a["display_name"] for a in resp.json()["agents"]]
    assert "Bot1" in names
    assert "Bot2" in names


@pytest.mark.asyncio
async def test_agents_mine_rejects_bearer_auth(client: AsyncClient, agent_headers: dict):
    resp = await client.get("/api/v1/agents/mine", headers=agent_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_device_approval_can_link_existing_agent(client: AsyncClient, human_session_cookie: str):
    start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "Existing",
            "model_slug": "openai/gpt-5",
            "runtime_kind": "codex-cli",
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
    agent_id = poll.json()["agent_id"]

    second_start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "Existing Again",
            "model_slug": "openai/gpt-5",
            "runtime_kind": "codex-cli",
        },
    )
    linked = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": human_session_cookie},
        json={"user_code": second_start.json()["user_code"], "agent_id": agent_id},
    )
    assert linked.status_code == 200
    assert linked.json()["agent_id"] == agent_id


@pytest.mark.asyncio
async def test_device_approval_rejects_model_runtime_mismatch(client: AsyncClient, human_session_cookie: str):
    start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "Mismatch",
            "model_slug": "openai/gpt-5",
            "runtime_kind": "codex-cli",
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
    agent_id = poll.json()["agent_id"]

    second_start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "Mismatch Again",
            "model_slug": "openai/gpt-4o",
            "runtime_kind": "openai-api",
        },
    )
    linked = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": human_session_cookie},
        json={"user_code": second_start.json()["user_code"], "agent_id": agent_id},
    )
    assert linked.status_code == 400
