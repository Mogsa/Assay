async def _create_owned_agent(client, human_session_cookie: str, *, name: str = "AutoAgent"):
    response = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": name,
            "model_slug": "openai/gpt-5",
            "runtime_kind": "codex-cli",
        },
    )
    assert response.status_code == 201
    approve = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": human_session_cookie},
        json={"user_code": response.json()["user_code"]},
    )
    assert approve.status_code == 200
    poll = await client.post(
        "/api/v1/cli/device/poll",
        json={"device_code": response.json()["device_code"]},
    )
    assert poll.status_code == 200
    return poll.json()


async def test_runtime_policy_defaults_are_visible_to_owner_and_agent(client, human_session_cookie: str):
    agent = await _create_owned_agent(client, human_session_cookie)

    owner_resp = await client.get(
        f"/api/v1/agents/{agent['agent_id']}/runtime-policy",
        cookies={"session": human_session_cookie},
    )
    assert owner_resp.status_code == 200
    assert owner_resp.json()["enabled"] is False
    assert owner_resp.json()["dry_run"] is True

    agent_resp = await client.get(
        f"/api/v1/agents/{agent['agent_id']}/runtime-policy",
        headers={"Authorization": f"Bearer {agent['access_token']}"},
    )
    assert agent_resp.status_code == 200
    assert agent_resp.json()["global_only"] is True


async def test_runtime_policy_update_persists(client, human_session_cookie: str):
    agent = await _create_owned_agent(client, human_session_cookie, name="MutablePolicy")
    update = await client.put(
        f"/api/v1/agents/{agent['agent_id']}/runtime-policy",
        cookies={"session": human_session_cookie},
        json={
            "enabled": True,
            "dry_run": False,
            "max_actions_per_hour": 2,
            "max_questions_per_day": 0,
            "max_answers_per_hour": 1,
            "max_reviews_per_hour": 1,
            "allow_question_asking": False,
            "allow_reposts": True,
            "allowed_community_ids": [],
            "global_only": True,
        },
    )
    assert update.status_code == 200
    assert update.json()["enabled"] is True
    assert update.json()["allow_reposts"] is True

    read_back = await client.get(
        f"/api/v1/agents/{agent['agent_id']}/runtime-policy",
        headers={"Authorization": f"Bearer {agent['access_token']}"},
    )
    assert read_back.status_code == 200
    assert read_back.json()["dry_run"] is False


async def test_autonomous_answer_requires_enabled_runtime_policy(
    client,
    human_session_cookie: str,
    second_agent_headers,
):
    question = await client.post(
        "/api/v1/questions",
        json={"title": "Needs policy", "body": "Body"},
        headers=second_agent_headers,
    )
    qid = question.json()["id"]
    agent = await _create_owned_agent(client, human_session_cookie, name="PolicyGate")

    blocked = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={"body": "Autonomous answer"},
        headers={
            "Authorization": f"Bearer {agent['access_token']}",
            "X-Assay-Execution-Mode": "autonomous",
        },
    )
    assert blocked.status_code == 403

    enable = await client.put(
        f"/api/v1/agents/{agent['agent_id']}/runtime-policy",
        cookies={"session": human_session_cookie},
        json={
            "enabled": True,
            "dry_run": True,
            "max_actions_per_hour": 6,
            "max_questions_per_day": 0,
            "max_answers_per_hour": 3,
            "max_reviews_per_hour": 6,
            "allow_question_asking": False,
            "allow_reposts": False,
            "allowed_community_ids": [],
            "global_only": True,
        },
    )
    assert enable.status_code == 200

    allowed = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={"body": "Autonomous answer"},
        headers={
            "Authorization": f"Bearer {agent['access_token']}",
            "X-Assay-Execution-Mode": "autonomous",
        },
    )
    assert allowed.status_code == 201
    assert allowed.json()["created_via"] == "autonomous"


async def test_autonomous_question_asking_respects_allow_question_asking(
    client,
    human_session_cookie: str,
):
    agent = await _create_owned_agent(client, human_session_cookie, name="QuestionGate")
    enable = await client.put(
        f"/api/v1/agents/{agent['agent_id']}/runtime-policy",
        cookies={"session": human_session_cookie},
        json={
            "enabled": True,
            "dry_run": True,
            "max_actions_per_hour": 6,
            "max_questions_per_day": 0,
            "max_answers_per_hour": 3,
            "max_reviews_per_hour": 6,
            "allow_question_asking": False,
            "allow_reposts": False,
            "allowed_community_ids": [],
            "global_only": True,
        },
    )
    assert enable.status_code == 200

    response = await client.post(
        "/api/v1/questions",
        json={"title": "Autonomous ask", "body": "Should be blocked"},
        headers={
            "Authorization": f"Bearer {agent['access_token']}",
            "X-Assay-Execution-Mode": "autonomous",
        },
    )
    assert response.status_code == 403
    assert "question asking" in response.json()["detail"].lower()
