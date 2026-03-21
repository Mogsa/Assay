import uuid


async def _create_question(client, headers):
    resp = await client.post(
        "/api/v1/questions",
        json={"title": "Test Q", "body": "Question body"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_answer(client, question_id, headers):
    resp = await client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"body": "Answer body"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# --- Task 2: Comments on questions ---


async def test_comment_on_question(client, agent_headers):
    qid = await _create_question(client, agent_headers)

    resp = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "Great question!"},
        headers=agent_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["body"] == "Great question!"
    assert data["target_type"] == "question"
    assert data["target_id"] == qid
    assert data["parent_id"] is None
    assert data["verdict"] is None


async def test_nested_comment(client, agent_headers, second_agent_headers):
    qid = await _create_question(client, agent_headers)

    parent = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "Top-level comment"},
        headers=agent_headers,
    )
    parent_id = parent.json()["id"]

    resp = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "Reply to comment", "parent_id": parent_id},
        headers=second_agent_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["parent_id"] == parent_id


async def test_reject_deep_nesting(client, agent_headers, second_agent_headers):
    qid = await _create_question(client, agent_headers)

    # Top-level comment
    c1 = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "Level 0"},
        headers=agent_headers,
    )
    c1_id = c1.json()["id"]

    # Reply (level 1 — allowed)
    c2 = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "Level 1", "parent_id": c1_id},
        headers=second_agent_headers,
    )
    c2_id = c2.json()["id"]

    # Reply to reply (level 2 — rejected)
    resp = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "Level 2", "parent_id": c2_id},
        headers=agent_headers,
    )
    assert resp.status_code == 400
    assert "nesting" in resp.json()["detail"].lower()


async def test_reject_parent_comment_from_different_target(
    client, agent_headers, second_agent_headers
):
    q1 = await _create_question(client, agent_headers)
    q2 = await _create_question(client, second_agent_headers)

    parent = await client.post(
        f"/api/v1/questions/{q1}/comments",
        json={"body": "Parent on q1"},
        headers=agent_headers,
    )
    parent_id = parent.json()["id"]

    resp = await client.post(
        f"/api/v1/questions/{q2}/comments",
        json={"body": "Reply on wrong question", "parent_id": parent_id},
        headers=second_agent_headers,
    )
    assert resp.status_code == 400
    assert "same target" in resp.json()["detail"].lower()


async def test_comment_on_nonexistent_question(client, agent_headers):
    fake_id = str(uuid.uuid4())
    resp = await client.post(
        f"/api/v1/questions/{fake_id}/comments",
        json={"body": "Hello?"},
        headers=agent_headers,
    )
    assert resp.status_code == 404


async def test_comment_requires_auth(client, agent_headers):
    qid = await _create_question(client, agent_headers)

    client.cookies.clear()
    resp = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "No auth"},
    )
    assert resp.status_code in (401, 403)


# --- Task 3: Comments on answers + verdicts ---


async def test_comment_on_answer(client, agent_headers, second_agent_headers):
    qid = await _create_question(client, agent_headers)
    aid = await _create_answer(client, qid, second_agent_headers)

    resp = await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "Nice answer!"},
        headers=agent_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["target_type"] == "answer"
    assert data["target_id"] == aid
    assert data["verdict"] is None


async def test_comment_with_verdict(client, agent_headers, second_agent_headers):
    qid = await _create_question(client, agent_headers)
    aid = await _create_answer(client, qid, second_agent_headers)

    resp = await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "Verified!", "verdict": "correct"},
        headers=agent_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["verdict"] == "correct"


async def test_invalid_verdict_rejected(client, agent_headers, second_agent_headers):
    qid = await _create_question(client, agent_headers)
    aid = await _create_answer(client, qid, second_agent_headers)

    resp = await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "Amazing!", "verdict": "amazing"},
        headers=agent_headers,
    )
    assert resp.status_code == 422


# --- Verdict behaviour ---


async def test_single_correct_verdict_does_not_close_question(
    client, agent_headers, second_agent_headers
):
    """One correct verdict is not enough to auto-close — need ≥2."""
    qid = await _create_question(client, agent_headers)
    aid = await _create_answer(client, qid, second_agent_headers)

    await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "This is correct.", "verdict": "correct"},
        headers=agent_headers,
    )

    q = await client.get(f"/api/v1/questions/{qid}")
    assert q.json()["status"] == "open"


async def test_two_correct_verdicts_do_not_auto_close_question(
    client, agent_headers, second_agent_headers, third_agent_headers
):
    """Auto-close is removed in v2 — two correct verdicts keep the question open."""
    qid = await _create_question(client, agent_headers)
    aid = await _create_answer(client, qid, second_agent_headers)

    await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "Looks right.", "verdict": "correct"},
        headers=agent_headers,
    )
    await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "Confirmed correct.", "verdict": "correct"},
        headers=third_agent_headers,
    )
    q = await client.get(f"/api/v1/questions/{qid}")
    assert q.json()["status"] == "open"


async def test_correct_plus_incorrect_does_not_close(
    client, agent_headers, second_agent_headers, third_agent_headers
):
    """Correct + incorrect = contested. Do not close."""
    qid = await _create_question(client, agent_headers)
    aid = await _create_answer(client, qid, second_agent_headers)

    await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "This is correct.", "verdict": "correct"},
        headers=agent_headers,
    )
    await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "No it is not.", "verdict": "incorrect"},
        headers=third_agent_headers,
    )

    q = await client.get(f"/api/v1/questions/{qid}")
    assert q.json()["status"] == "open"


async def test_correct_verdict_same_author_does_not_close(
    client, agent_headers, second_agent_headers
):
    # agent_a creates question, agent_b creates answer
    qid = await _create_question(client, agent_headers)
    aid = await _create_answer(client, qid, second_agent_headers)

    # agent_b reviews their OWN answer with verdict="correct"
    resp = await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "I think I got it right.", "verdict": "correct"},
        headers=second_agent_headers,
    )
    assert resp.status_code == 201

    # Question should remain "open" — self-review must not trigger auto-close
    q = await client.get(f"/api/v1/questions/{qid}")
    assert q.status_code == 200
    assert q.json()["status"] == "open"
