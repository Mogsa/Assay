from assay import main as main_module


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
    assert "Authorization: Bearer $ASSAY_API_KEY" in body
    assert "/questions/{id}/answers" in body
    assert "/agents/me" in body
    assert "/questions/{id}/preview" in body
    assert "view=scan" in body
    assert "/api/v1/cli/device/start" not in body
    assert "/api/v1/cli/token/refresh" not in body


async def test_agent_guide_covers_setup_and_loop(client):
    resp = await client.get("/agent-guide")
    assert resp.status_code == 200
    body = resp.text
    assert "skill.md" in body
    assert "setup command" in body.lower()
    assert "loop command" in body.lower()
    assert "/api/v1/cli/device" not in body
    assert "assay connect" not in body


async def test_skill_document_and_version_update_without_restart(
    client, monkeypatch, tmp_path
):
    skill_path = tmp_path / "skill.md"
    skill_path.write_text("first version content", encoding="utf-8")
    monkeypatch.setattr(main_module, "SKILL_PATH", skill_path)

    first_skill = await client.get("/skill.md")
    first_version = await client.get("/api/v1/skill/version")

    skill_path.write_text("second version content", encoding="utf-8")

    second_skill = await client.get("/skill.md")
    second_version = await client.get("/api/v1/skill/version")

    assert first_skill.status_code == 200
    assert second_skill.status_code == 200
    assert first_skill.text != second_skill.text
    assert first_version.json()["version"] != second_version.json()["version"]
