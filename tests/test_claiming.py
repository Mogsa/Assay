from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import update as sa_update

from assay.models.agent import Agent


@pytest.mark.asyncio
async def test_register_returns_claim_token(client: AsyncClient):
    resp = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "ClaimMe",
            "model_slug": "anthropic/claude-opus-4",
            "runtime_kind": "claude-cli",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "api_key" in data
    assert "claim_token" in data
    assert "claim_url" not in data


@pytest.mark.asyncio
async def test_claim_agent(client: AsyncClient):
    reg_resp = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "MyBot",
            "model_slug": "anthropic/claude-sonnet-4",
            "runtime_kind": "claude-cli",
        },
    )
    claim_token = reg_resp.json()["claim_token"]

    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "owner@example.com", "password": "securepass123", "display_name": "Owner"},
    )
    session_cookie = signup_resp.cookies.get("session")

    claim_resp = await client.post(
        f"/api/v1/agents/claim/{claim_token}",
        cookies={"session": session_cookie},
    )
    assert claim_resp.status_code == 200
    assert claim_resp.json()["claim_status"] == "claimed"
    assert claim_resp.json()["display_name"] == "MyBot"


@pytest.mark.asyncio
async def test_claim_rejects_bearer_auth(client: AsyncClient):
    reg_resp = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "SelfClaim",
            "model_slug": "anthropic/claude-sonnet-4",
            "runtime_kind": "claude-cli",
        },
    )
    claim_token = reg_resp.json()["claim_token"]
    api_key = reg_resp.json()["api_key"]

    resp = await client.post(
        f"/api/v1/agents/claim/{claim_token}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_claim_already_claimed_returns_409(client: AsyncClient):
    reg_resp = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "Taken",
            "model_slug": "anthropic/claude-sonnet-4",
            "runtime_kind": "claude-cli",
        },
    )
    claim_token = reg_resp.json()["claim_token"]

    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "first@example.com", "password": "securepass123", "display_name": "First"},
    )
    cookie = signup_resp.cookies.get("session")

    await client.post(f"/api/v1/agents/claim/{claim_token}", cookies={"session": cookie})
    resp2 = await client.post(f"/api/v1/agents/claim/{claim_token}", cookies={"session": cookie})
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_claim_invalid_token_returns_404(client: AsyncClient):
    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "nobody@example.com", "password": "securepass123", "display_name": "Nobody"},
    )
    cookie = signup_resp.cookies.get("session")

    resp = await client.post(
        "/api/v1/agents/claim/bogus-token-value",
        cookies={"session": cookie},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_agents_mine_lists_claimed_agents(client: AsyncClient):
    reg1 = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "Bot1",
            "model_slug": "openai/gpt-4o",
            "runtime_kind": "openai-api",
        },
    )
    reg2 = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "Bot2",
            "model_slug": "anthropic/claude-opus-4",
            "runtime_kind": "claude-cli",
        },
    )

    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "multi@example.com", "password": "securepass123", "display_name": "Multi"},
    )
    cookie = signup_resp.cookies.get("session")

    await client.post(f"/api/v1/agents/claim/{reg1.json()['claim_token']}", cookies={"session": cookie})
    await client.post(f"/api/v1/agents/claim/{reg2.json()['claim_token']}", cookies={"session": cookie})

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
async def test_claim_expired_token_returns_410(client: AsyncClient, db):
    reg_resp = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "ExpiredBot",
            "model_slug": "anthropic/claude-sonnet-4",
            "runtime_kind": "claude-cli",
        },
    )
    claim_token = reg_resp.json()["claim_token"]
    agent_id = reg_resp.json()["agent_id"]

    await db.execute(
        sa_update(Agent)
        .where(Agent.id == agent_id)
        .values(claim_token_expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc))
    )
    await db.flush()

    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "expired@example.com", "password": "securepass123", "display_name": "Expired"},
    )
    cookie = signup_resp.cookies.get("session")

    resp = await client.post(
        f"/api/v1/agents/claim/{claim_token}",
        cookies={"session": cookie},
    )
    assert resp.status_code == 410


@pytest.mark.asyncio
async def test_unclaimed_agent_cannot_create_community(
    client: AsyncClient,
    unclaimed_agent_headers: dict[str, str],
):
    resp = await client.post(
        "/api/v1/communities",
        json={
            "name": "blocked-community",
            "display_name": "Blocked Community",
            "description": "nope",
        },
        headers=unclaimed_agent_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_unclaimed_agent_cannot_join_or_leave_community(
    client: AsyncClient,
    agent_headers: dict[str, str],
    unclaimed_agent_headers: dict[str, str],
):
    create_resp = await client.post(
        "/api/v1/communities",
        json={"name": "claim-gated", "display_name": "Claim Gated", "description": "test"},
        headers=agent_headers,
    )
    community_id = create_resp.json()["id"]

    join_resp = await client.post(
        f"/api/v1/communities/{community_id}/join",
        headers=unclaimed_agent_headers,
    )
    assert join_resp.status_code == 403

    leave_resp = await client.delete(
        f"/api/v1/communities/{community_id}/leave",
        headers=unclaimed_agent_headers,
    )
    assert leave_resp.status_code == 403


@pytest.mark.asyncio
async def test_unclaimed_agent_cannot_create_question(
    client: AsyncClient,
    unclaimed_agent_headers: dict[str, str],
):
    resp = await client.post(
        "/api/v1/questions",
        json={"title": "Blocked", "body": "Not claimed"},
        headers=unclaimed_agent_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_unclaimed_agent_cannot_create_answer(
    client: AsyncClient,
    agent_headers: dict[str, str],
    unclaimed_agent_headers: dict[str, str],
):
    question_resp = await client.post(
        "/api/v1/questions",
        json={"title": "Claimed Q", "body": "Created by claimed agent"},
        headers=agent_headers,
    )
    question_id = question_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"body": "I should not be allowed"},
        headers=unclaimed_agent_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_unclaimed_agent_cannot_vote_on_question(
    client: AsyncClient,
    agent_headers: dict[str, str],
    unclaimed_agent_headers: dict[str, str],
):
    question_resp = await client.post(
        "/api/v1/questions",
        json={"title": "Claimed Q", "body": "Created by claimed agent"},
        headers=agent_headers,
    )
    question_id = question_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/questions/{question_id}/vote",
        json={"value": 1},
        headers=unclaimed_agent_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_unclaimed_agent_cannot_vote_on_answer(
    client: AsyncClient,
    agent_headers: dict[str, str],
    second_agent_headers: dict[str, str],
    unclaimed_agent_headers: dict[str, str],
):
    question_resp = await client.post(
        "/api/v1/questions",
        json={"title": "Claimed Q", "body": "Created by claimed agent"},
        headers=agent_headers,
    )
    question_id = question_resp.json()["id"]

    answer_resp = await client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"body": "Created by another claimed agent"},
        headers=second_agent_headers,
    )
    answer_id = answer_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/answers/{answer_id}/vote",
        json={"value": 1},
        headers=unclaimed_agent_headers,
    )
    assert resp.status_code == 403
