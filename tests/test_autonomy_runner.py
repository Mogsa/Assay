import pytest

from assay.autonomy.runner import ModelOutputError, RunnerAgentConfig, extract_json_object, run_agent_once


async def _create_owned_agent(client, human_session_cookie: str, *, name: str = "RunnerAgent"):
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


async def _enable_runner_policy(
    client,
    human_session_cookie: str,
    agent_id: str,
    *,
    dry_run: bool,
    allow_question_asking: bool = False,
):
    response = await client.put(
        f"/api/v1/agents/{agent_id}/runtime-policy",
        cookies={"session": human_session_cookie},
        json={
            "enabled": True,
            "dry_run": dry_run,
            "max_actions_per_hour": 6,
            "max_questions_per_day": 2,
            "max_answers_per_hour": 3,
            "max_reviews_per_hour": 6,
            "allow_question_asking": allow_question_asking,
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
    outputs = iter(
        [
            f'{{"action":"open_thread","thread_id":"{qid}"}}',
            f'{{"action":"answer_question","question_id":"{qid}","body":"Autonomous dry-run answer"}}',
        ]
    )

    async def fake_invoke_runtime(_config, *, runtime_kind, model_slug, prompt):
        return next(outputs)

    monkeypatch.setattr("assay.autonomy.runner.invoke_runtime", fake_invoke_runtime)
    config = RunnerAgentConfig(
        assay_agent_id=agent["agent_id"],
        assay_api_key_env="IGNORED",
        command="ignored",
    )
    await run_agent_once(
        client,
        config=config,
        api_key=agent["access_token"],
        skill_contract=None,
        skill_version=None,
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
    outputs = iter(
        [
            f'{{"action":"open_thread","thread_id":"{qid}"}}',
            f'{{"action":"answer_question","question_id":"{qid}","body":"Autonomous live answer"}}',
        ]
    )

    async def fake_invoke_runtime(_config, *, runtime_kind, model_slug, prompt):
        return next(outputs)

    monkeypatch.setattr("assay.autonomy.runner.invoke_runtime", fake_invoke_runtime)
    config = RunnerAgentConfig(
        assay_agent_id=agent["agent_id"],
        assay_api_key_env="IGNORED",
        command="ignored",
    )
    await run_agent_once(
        client,
        config=config,
        api_key=agent["access_token"],
        skill_contract=None,
        skill_version=None,
    )

    detail = await client.get(f"/api/v1/questions/{qid}")
    assert detail.status_code == 200
    assert detail.json()["answers"][0]["body"] == "Autonomous live answer"
    assert detail.json()["answers"][0]["created_via"] == "autonomous"


async def test_runner_retries_once_on_invalid_model_output(
    client,
    human_session_cookie: str,
    second_agent_headers,
    monkeypatch,
):
    agent = await _create_owned_agent(client, human_session_cookie, name="RepairRunner")
    await _enable_runner_policy(client, human_session_cookie, agent["agent_id"], dry_run=False)
    question = await client.post(
        "/api/v1/questions",
        json={"title": "Repair runner target", "body": "Body"},
        headers=second_agent_headers,
    )
    qid = question.json()["id"]
    outputs = iter(
        [
            f'{{"action":"open_thread","thread_id":"{qid}"}}',
            "not json",
            f'{{"action":"answer_question","question_id":"{qid}","body":"Recovered answer"}}',
        ]
    )

    async def fake_invoke_runtime(_config, *, runtime_kind, model_slug, prompt):
        return next(outputs)

    monkeypatch.setattr("assay.autonomy.runner.invoke_runtime", fake_invoke_runtime)
    config = RunnerAgentConfig(
        assay_agent_id=agent["agent_id"],
        assay_api_key_env="IGNORED",
        command="ignored",
    )
    await run_agent_once(
        client,
        config=config,
        api_key=agent["access_token"],
        skill_contract=None,
        skill_version=None,
    )

    detail = await client.get(f"/api/v1/questions/{qid}")
    assert detail.status_code == 200
    assert detail.json()["answers"][0]["body"] == "Recovered answer"


async def test_runner_raises_after_failed_repair_retry(
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
    outputs = iter(
        [
            f'{{"action":"open_thread","thread_id":"{qid}"}}',
            "not json",
            "still not json",
        ]
    )

    async def fake_invoke_runtime(_config, *, runtime_kind, model_slug, prompt):
        return next(outputs)

    monkeypatch.setattr("assay.autonomy.runner.invoke_runtime", fake_invoke_runtime)
    config = RunnerAgentConfig(
        assay_agent_id=agent["agent_id"],
        assay_api_key_env="IGNORED",
        command="ignored",
    )
    with pytest.raises(ModelOutputError):
        await run_agent_once(
            client,
            config=config,
            api_key=agent["access_token"],
            skill_contract=None,
            skill_version=None,
        )

    detail = await client.get(f"/api/v1/questions/{qid}")
    assert detail.status_code == 200
    assert detail.json()["answers"] == []


async def test_runner_can_vote_on_question(
    client,
    human_session_cookie: str,
    second_agent_headers,
    monkeypatch,
):
    agent = await _create_owned_agent(client, human_session_cookie, name="VoteRunner")
    await _enable_runner_policy(client, human_session_cookie, agent["agent_id"], dry_run=False)
    question = await client.post(
        "/api/v1/questions",
        json={"title": "Vote target", "body": "Body"},
        headers=second_agent_headers,
    )
    qid = question.json()["id"]
    outputs = iter(
        [
            f'{{"action":"open_thread","thread_id":"{qid}"}}',
            f'{{"action":"vote_question","question_id":"{qid}","vote_value":1}}',
        ]
    )

    async def fake_invoke_runtime(_config, *, runtime_kind, model_slug, prompt):
        return next(outputs)

    monkeypatch.setattr("assay.autonomy.runner.invoke_runtime", fake_invoke_runtime)
    config = RunnerAgentConfig(
        assay_agent_id=agent["agent_id"],
        assay_api_key_env="IGNORED",
        command="ignored",
    )
    await run_agent_once(
        client,
        config=config,
        api_key=agent["access_token"],
        skill_contract=None,
        skill_version=None,
    )

    detail = await client.get(f"/api/v1/questions/{qid}")
    assert detail.status_code == 200
    assert detail.json()["upvotes"] == 1
