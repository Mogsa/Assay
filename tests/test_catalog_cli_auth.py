async def test_create_agent_requires_human_session(client):
    response = await client.post(
        "/api/v1/agents",
        json={
            "display_name": "NoSession",
            "model_slug": "openai/gpt-5",
            "runtime_kind": "codex-cli",
        },
    )
    assert response.status_code == 401


async def test_create_agent_validates_known_model(client, human_session_cookie: str):
    response = await client.post(
        "/api/v1/agents",
        cookies={"session": human_session_cookie},
        json={
            "display_name": "UnknownModel",
            "model_slug": "unknown/model",
            "runtime_kind": "codex-cli",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown model slug"


async def test_create_agent_validates_known_runtime(client, human_session_cookie: str):
    response = await client.post(
        "/api/v1/agents",
        cookies={"session": human_session_cookie},
        json={
            "display_name": "UnknownRuntime",
            "model_slug": "openai/gpt-5",
            "runtime_kind": "unknown-runtime",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown runtime kind"


async def test_skill_version_endpoint(client):
    version = await client.get("/api/v1/skill/version")
    assert version.status_code == 200
    assert len(version.json()["version"]) == 12


async def test_skill_document_uses_api_key_flow(client):
    resp = await client.get("/skill.md")
    assert resp.status_code == 200
    body = resp.text
    assert "Authorization: Bearer sk_" in body
    assert "/api/v1/questions/{question_id}/answers" in body
    assert "/api/v1/agents/me" in body
    assert "/api/v1/cli/device/start" not in body
    assert "/api/v1/cli/token/refresh" not in body


async def test_agent_guide_matches_real_routes(client):
    resp = await client.get("/agent-guide")
    assert resp.status_code == 200
    body = resp.text
    assert "/api/v1/agents/{agent_id}/api-key" in body
    assert "/api/v1/agents/me" in body
    assert "/api/v1/cli/device" not in body
    assert "assay connect" not in body
