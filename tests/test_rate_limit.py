from contextlib import asynccontextmanager

import pytest
from httpx import ASGITransport, AsyncClient

from assay.database import get_db
from assay.main import app
from assay.rate_limit import limiter


@asynccontextmanager
async def rate_limited_client(db):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    limiter.enabled = True
    limiter.reset()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client
    finally:
        limiter.enabled = False
        limiter.reset()
        app.dependency_overrides.clear()


async def _create_agent_for_rate_limit_test(client: AsyncClient) -> dict[str, str]:
    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "ratelimit-owner@example.com",
            "password": "securepass123",
            "display_name": "RateLimitOwner",
        },
    )
    session_cookie = signup_resp.cookies.get("session")
    create_resp = await client.post(
        "/api/v1/agents",
        cookies={"session": session_cookie},
        json={
            "display_name": "RateLimitedAgent",
            "model_slug": "anthropic/claude-opus-4-6",
            "runtime_kind": "claude-cli",
        },
    )
    assert create_resp.status_code == 201
    return {"Authorization": f"Bearer {create_resp.json()['api_key']}"}


@pytest.mark.asyncio
async def test_create_agent_rate_limit_enforced_with_headers(db):
    async with rate_limited_client(db) as client:
        signup_resp = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "ratelimit-create@example.com",
                "password": "securepass123",
                "display_name": "RateLimitCreate",
            },
        )
        session_cookie = signup_resp.cookies.get("session")
        responses = []
        for i in range(11):
            responses.append(
                await client.post(
                    "/api/v1/agents",
                    cookies={"session": session_cookie},
                    json={
                        "display_name": f"Spam{i}",
                        "model_slug": "openai/gpt-4o",
                        "runtime_kind": "openai-api",
                    },
                )
            )

    assert all(resp.status_code == 201 for resp in responses[:10])
    assert responses[10].status_code == 429
    assert responses[0].headers["X-RateLimit-Limit"] == "10"
    assert "X-RateLimit-Remaining" in responses[0].headers
    assert "X-RateLimit-Reset" in responses[0].headers


@pytest.mark.asyncio
async def test_create_question_rate_limit_enforced(db):
    async with rate_limited_client(db) as client:
        agent_headers = await _create_agent_for_rate_limit_test(client)
        responses = []
        for i in range(3):
            responses.append(
                await client.post(
                    "/api/v1/questions",
                    json={"title": f"Rate Limit {i}", "body": "Body"},
                    headers=agent_headers,
                )
            )

    assert [resp.status_code for resp in responses] == [201, 201, 429]
    assert responses[0].headers["X-RateLimit-Limit"] == "2"


@pytest.mark.asyncio
async def test_list_questions_rate_limit_enforced(db):
    async with rate_limited_client(db) as client:
        agent_headers = await _create_agent_for_rate_limit_test(client)
        seed_resp = await client.post(
            "/api/v1/questions",
            json={"title": "Seed", "body": "Body"},
            headers=agent_headers,
        )
        assert seed_resp.status_code == 201

        responses = []
        for _ in range(61):
            responses.append(await client.get("/api/v1/questions", headers=agent_headers))

    assert all(resp.status_code == 200 for resp in responses[:60])
    assert responses[60].status_code == 429
    assert responses[0].headers["X-RateLimit-Limit"] == "60"
