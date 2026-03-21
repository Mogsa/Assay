async def test_post_answer(client, agent_headers):
    q = await client.post(
        "/api/v1/questions",
        json={
            "title": "Q1",
            "body": "Body",
        },
        headers=agent_headers,
    )
    qid = q.json()["id"]

    resp = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={
            "body": "Here is my detailed answer.",
        },
        headers=agent_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["question_id"] == qid


async def test_one_answer_per_agent_per_question(client, agent_headers):
    q = await client.post(
        "/api/v1/questions",
        json={
            "title": "Q1",
            "body": "Body",
        },
        headers=agent_headers,
    )
    qid = q.json()["id"]

    await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={
            "body": "First answer",
        },
        headers=agent_headers,
    )
    resp = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={
            "body": "Second answer",
        },
        headers=agent_headers,
    )
    assert resp.status_code == 409


async def test_different_agents_can_answer(client, agent_headers, second_agent_headers):
    q = await client.post(
        "/api/v1/questions",
        json={
            "title": "Q1",
            "body": "Body",
        },
        headers=agent_headers,
    )
    qid = q.json()["id"]

    r1 = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={
            "body": "Agent 1 answer",
        },
        headers=agent_headers,
    )
    r2 = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={
            "body": "Agent 2 answer",
        },
        headers=second_agent_headers,
    )
    assert r1.status_code == 201
    assert r2.status_code == 201


async def test_get_answer_by_id(client, agent_headers):
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Q1", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    created = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={"body": "My detailed answer"},
        headers=agent_headers,
    )
    aid = created.json()["id"]

    resp = await client.get(f"/api/v1/answers/{aid}", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == aid
    assert data["question_id"] == qid
    assert data["body"] == "My detailed answer"
    assert "author" in data
    assert "frontier_score" in data
    assert "created_at" in data


async def test_get_answer_not_found(client, agent_headers):
    import uuid

    resp = await client.get(
        f"/api/v1/answers/{uuid.uuid4()}", headers=agent_headers
    )
    assert resp.status_code == 404


async def test_answer_appears_in_question_detail(client, agent_headers):
    q = await client.post(
        "/api/v1/questions",
        json={
            "title": "Q1",
            "body": "Body",
        },
        headers=agent_headers,
    )
    qid = q.json()["id"]

    await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={
            "body": "My answer",
        },
        headers=agent_headers,
    )

    detail = await client.get(f"/api/v1/questions/{qid}", headers=agent_headers)
    assert len(detail.json()["answers"]) == 1
    assert detail.json()["answers"][0]["body"] == "My answer"
