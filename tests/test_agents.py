from sqlalchemy import select

from assay.models.agent import Agent


async def test_create_agent_returns_api_key(client, human_session_cookie: str):
    response = await client.post(
        "/api/v1/agents",
        cookies={"session": human_session_cookie},
        json={
            "display_name": "MyAgent",
            "model_slug": "anthropic/claude-opus-4-6",
            "runtime_kind": "claude-cli",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["api_key"].startswith("sk_")
    assert payload["model_slug"] == "anthropic/claude-opus-4-6"
    assert payload["runtime_kind"] == "claude-cli"


async def test_me_returns_profile(client, agent_headers):
    resp = await client.get("/api/v1/agents/me", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "TestAgent"
    assert data["question_karma"] == 0
    assert data["answer_karma"] == 0
    assert data["review_karma"] == 0


async def test_me_updates_last_active_at(client, db, human_session_cookie: str):
    created = await client.post(
        "/api/v1/agents",
        cookies={"session": human_session_cookie},
        json={
            "display_name": "ActiveAgent",
            "model_slug": "openai/gpt-5",
            "runtime_kind": "codex-cli",
        },
    )
    assert created.status_code == 201
    agent_id = created.json()["agent_id"]

    before = await db.get(Agent, agent_id)
    assert before.last_active_at is None

    me = await client.get(
        "/api/v1/agents/me",
        headers={"Authorization": f"Bearer {created.json()['api_key']}"},
    )
    assert me.status_code == 200

    refreshed = await db.get(Agent, agent_id)
    assert refreshed.last_active_at is not None


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


async def test_activity_summary_aggregates_recent_work(client, agent_headers, second_agent_headers):
    me = await client.get("/api/v1/agents/me", headers=agent_headers)
    agent_id = me.json()["id"]

    own_question = await client.post(
        "/api/v1/questions",
        json={"title": "Own thread", "body": "Body"},
        headers=agent_headers,
    )
    assert own_question.status_code == 201
    own_question_id = own_question.json()["id"]

    external_question = await client.post(
        "/api/v1/questions",
        json={"title": "External thread", "body": "Body"},
        headers=second_agent_headers,
    )
    assert external_question.status_code == 201
    external_question_id = external_question.json()["id"]

    answer_on_own = await client.post(
        f"/api/v1/questions/{own_question_id}/answers",
        json={"body": "Counterpoint"},
        headers=second_agent_headers,
    )
    assert answer_on_own.status_code == 201
    answer_id = answer_on_own.json()["id"]

    autonomous_headers = {
        **agent_headers,
        "X-Assay-Execution-Mode": "autonomous",
    }

    answer = await client.post(
        f"/api/v1/questions/{external_question_id}/answers",
        json={"body": "Autonomous answer"},
        headers=autonomous_headers,
    )
    assert answer.status_code == 201

    review = await client.post(
        f"/api/v1/answers/{answer_id}/comments",
        json={"body": "This misses the edge case.", "verdict": "incorrect"},
        headers=autonomous_headers,
    )
    assert review.status_code == 201

    summary = await client.get(
        f"/api/v1/agents/{agent_id}/activity/summary",
        params={"hours": 1, "limit": 10},
    )
    assert summary.status_code == 200
    payload = summary.json()

    assert payload["total_items"] == 3
    assert payload["is_truncated"] is False
    assert payload["counts"] == {"questions": 1, "answers": 1, "comments": 1}
    assert payload["modes"] == {"manual": 1, "autonomous": 2}
    assert payload["verdicts"]["incorrect"] == 1
    assert payload["distinct_threads"] == 2
    assert payload["top_threads"][0]["title"] == "Own thread"
    assert payload["top_threads"][0]["interaction_count"] == 2
    assert len(payload["sessions"]) >= 1
    assert "3 interactions" in payload["summary"]


async def test_activity_summary_marks_truncated_results(client, agent_headers):
    me = await client.get("/api/v1/agents/me", headers=agent_headers)
    agent_id = me.json()["id"]

    first = await client.post(
        "/api/v1/questions",
        json={"title": "First", "body": "Body"},
        headers=agent_headers,
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/questions",
        json={"title": "Second", "body": "Body"},
        headers=agent_headers,
    )
    assert second.status_code == 201

    summary = await client.get(
        f"/api/v1/agents/{agent_id}/activity/summary",
        params={"hours": 1, "limit": 1},
    )
    assert summary.status_code == 200
    payload = summary.json()

    assert payload["total_items"] == 1
    assert payload["is_truncated"] is True
    assert payload["summary"].startswith("Summarized the most recent 1 interactions")


async def test_owner_can_rotate_agent_api_key(client, human_session_cookie: str, db):
    created = await client.post(
        "/api/v1/agents",
        cookies={"session": human_session_cookie},
        json={
            "display_name": "Rotatable",
            "model_slug": "openai/gpt-5",
            "runtime_kind": "openai-api",
        },
    )
    assert created.status_code == 201
    agent_id = created.json()["agent_id"]
    old_key = created.json()["api_key"]

    rotated = await client.post(
        f"/api/v1/agents/{agent_id}/api-key",
        cookies={"session": human_session_cookie},
    )
    assert rotated.status_code == 200
    new_key = rotated.json()["api_key"]
    assert new_key != old_key

    old_me = await client.get("/api/v1/agents/me", headers={"Authorization": f"Bearer {old_key}"})
    assert old_me.status_code == 401

    new_me = await client.get("/api/v1/agents/me", headers={"Authorization": f"Bearer {new_key}"})
    assert new_me.status_code == 200

    agent = await db.scalar(select(Agent).where(Agent.id == agent_id))
    assert agent is not None
    assert agent.api_key_hash is not None


async def test_mine_includes_last_active_at(client, db, human_session_cookie: str):
    created = await client.post(
        "/api/v1/agents",
        cookies={"session": human_session_cookie},
        json={
            "display_name": "TimestampAgent",
            "model_slug": "anthropic/claude-opus-4-6",
            "runtime_kind": "claude-cli",
        },
    )
    assert created.status_code == 201
    api_key = created.json()["api_key"]

    # Make an API call as the agent to set last_active_at
    await client.get("/api/v1/agents/me", headers={"Authorization": f"Bearer {api_key}"})

    resp = await client.get("/api/v1/agents/mine", cookies={"session": human_session_cookie})
    assert resp.status_code == 200
    agents = resp.json()["agents"]
    agent = next(a for a in agents if a["display_name"] == "TimestampAgent")
    assert "last_active_at" in agent
    assert agent["last_active_at"] is not None


async def test_activity_includes_verdict(client, agent_headers, second_agent_headers):
    # agent_a creates question, agent_b creates answer, agent_a reviews with verdict
    agent_a_me = await client.get("/api/v1/agents/me", headers=agent_headers)
    agent_a_id = agent_a_me.json()["id"]

    question = await client.post(
        "/api/v1/questions",
        json={"title": "Verdict activity question", "body": "Body"},
        headers=agent_headers,
    )
    assert question.status_code == 201
    qid = question.json()["id"]

    answer = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={"body": "An answer"},
        headers=second_agent_headers,
    )
    assert answer.status_code == 201
    aid = answer.json()["id"]

    review = await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "Looks correct to me.", "verdict": "correct"},
        headers=agent_headers,
    )
    assert review.status_code == 201

    activity = await client.get(f"/api/v1/agents/{agent_a_id}/activity")
    assert activity.status_code == 200
    items = activity.json()["items"]

    comment_items = [i for i in items if i["item_type"] == "comment"]
    assert len(comment_items) >= 1
    assert comment_items[0]["verdict"] == "correct"


async def test_registry_returns_models_and_runtimes(client):
    resp = await client.get("/api/v1/agents/registry")
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data
    assert "runtimes" in data
    assert len(data["models"]) >= 13
    assert len(data["runtimes"]) >= 6
    first_model = data["models"][0]
    assert "slug" in first_model
    assert "display_name" in first_model
    assert "provider" in first_model
    first_runtime = data["runtimes"][0]
    assert "slug" in first_runtime
    assert "display_name" in first_runtime
