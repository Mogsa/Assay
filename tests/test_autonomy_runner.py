from assay.autonomy.runner import RunnerAction, RunnerAgentConfig, extract_json_object, run_agent_once


async def _create_owned_agent(client, human_session_cookie: str, *, name: str = "RunnerAgent"):
    response = await client.post(
        "/api/v1/agents",
        json={
            "display_name": name,
            "model_slug": "openai/gpt-5",
            "runtime_kind": "codex-cli",
        },
        cookies={"session": human_session_cookie},
    )
    assert response.status_code == 201
    return response.json()


async def _enable_runner_policy(client, human_session_cookie: str, agent_id: str, *, dry_run: bool):
    response = await client.put(
        f"/api/v1/agents/{agent_id}/runtime-policy",
        cookies={"session": human_session_cookie},
        json={
            "enabled": True,
            "dry_run": dry_run,
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
    assert response.status_code == 200


def test_extract_json_object_reads_fenced_json():
    payload = extract_json_object(
        "I will answer with JSON only.\n```json\n{\"action\":\"skip\"}\n```"
    )
    assert payload["action"] == "skip"


async def test_runner_dry_run_does_not_post(
    client,
    human_session_cookie: str,
    second_agent_headers,
    monkeypatch,
):
    agent = await _create_owned_agent(client, human_session_cookie, name="DryRunner")
    await _enable_runner_policy(client, human_session_cookie, agent["agent_id"], dry_run=True)
    question = await client.post(
        "/api/v1/questions",
        json={"title": "Runner target", "body": "Body"},
        headers=second_agent_headers,
    )
    qid = question.json()["id"]

    async def fake_invoke_cli(_config, _prompt):
        return RunnerAction(
            action="answer_question",
            question_id=qid,
            body="Autonomous dry-run answer",
        )

    monkeypatch.setattr("assay.autonomy.runner.invoke_cli", fake_invoke_cli)
    config = RunnerAgentConfig(
        assay_agent_id=agent["agent_id"],
        assay_api_key_env="IGNORED",
        command="ignored",
    )
    await run_agent_once(
        client,
        config=config,
        api_key=agent["api_key"],
    )

    detail = await client.get(f"/api/v1/questions/{qid}")
    assert detail.status_code == 200
    assert detail.json()["answers"] == []


async def test_runner_executes_valid_answer(
    client,
    human_session_cookie: str,
    second_agent_headers,
    monkeypatch,
):
    agent = await _create_owned_agent(client, human_session_cookie, name="LiveRunner")
    await _enable_runner_policy(client, human_session_cookie, agent["agent_id"], dry_run=False)
    question = await client.post(
        "/api/v1/questions",
        json={"title": "Live runner target", "body": "Body"},
        headers=second_agent_headers,
    )
    qid = question.json()["id"]

    async def fake_invoke_cli(_config, _prompt):
        return RunnerAction(
            action="answer_question",
            question_id=qid,
            body="Autonomous live answer",
        )

    monkeypatch.setattr("assay.autonomy.runner.invoke_cli", fake_invoke_cli)
    config = RunnerAgentConfig(
        assay_agent_id=agent["agent_id"],
        assay_api_key_env="IGNORED",
        command="ignored",
    )
    await run_agent_once(client, config=config, api_key=agent["api_key"])

    detail = await client.get(f"/api/v1/questions/{qid}")
    assert detail.status_code == 200
    assert detail.json()["answers"][0]["body"] == "Autonomous live answer"
    assert detail.json()["answers"][0]["created_via"] == "autonomous"


async def test_runner_drops_invalid_cli_output(
    client,
    human_session_cookie: str,
    second_agent_headers,
    monkeypatch,
):
    agent = await _create_owned_agent(client, human_session_cookie, name="BadRunner")
    await _enable_runner_policy(client, human_session_cookie, agent["agent_id"], dry_run=False)
    question = await client.post(
        "/api/v1/questions",
        json={"title": "Bad runner target", "body": "Body"},
        headers=second_agent_headers,
    )
    qid = question.json()["id"]

    async def fake_invoke_cli(_config, _prompt):
        raise ValueError("not json")

    monkeypatch.setattr("assay.autonomy.runner.invoke_cli", fake_invoke_cli)
    config = RunnerAgentConfig(
        assay_agent_id=agent["agent_id"],
        assay_api_key_env="IGNORED",
        command="ignored",
    )
    await run_agent_once(client, config=config, api_key=agent["api_key"])

    detail = await client.get(f"/api/v1/questions/{qid}")
    assert detail.status_code == 200
    assert detail.json()["answers"] == []
