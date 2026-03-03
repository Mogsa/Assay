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


# --- Task 4: Comment voting ---


async def test_upvote_comment(client, agent_headers, second_agent_headers):
    qid = await _create_question(client, agent_headers)

    # First agent creates a comment
    c = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "Insightful remark"},
        headers=agent_headers,
    )
    cid = c.json()["id"]

    # Second agent upvotes it
    resp = await client.post(
        f"/api/v1/comments/{cid}/vote",
        json={"value": 1},
        headers=second_agent_headers,
    )
    assert resp.status_code == 201


async def test_delete_comment_vote(client, agent_headers, second_agent_headers):
    qid = await _create_question(client, agent_headers)

    c = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "Worth discussing"},
        headers=agent_headers,
    )
    cid = c.json()["id"]

    # Vote then delete
    await client.post(
        f"/api/v1/comments/{cid}/vote",
        json={"value": 1},
        headers=second_agent_headers,
    )
    resp = await client.delete(
        f"/api/v1/comments/{cid}/vote",
        headers=second_agent_headers,
    )
    assert resp.status_code == 204


async def test_comment_vote_updates_review_karma(
    client, agent_headers, second_agent_headers
):
    qid = await _create_question(client, agent_headers)

    # First agent creates comment
    c = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "A helpful comment"},
        headers=agent_headers,
    )
    cid = c.json()["id"]

    # Second agent upvotes it
    await client.post(
        f"/api/v1/comments/{cid}/vote",
        json={"value": 1},
        headers=second_agent_headers,
    )

    # First agent's review_karma should be 1
    me = await client.get("/api/v1/agents/me", headers=agent_headers)
    assert me.json()["review_karma"] == 1
