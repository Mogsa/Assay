async def test_upvote_question(client, agent_headers, second_agent_headers):
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
        f"/api/v1/questions/{qid}/vote",
        json={
            "value": 1,
        },
        headers=second_agent_headers,
    )
    assert resp.status_code == 201

    detail = await client.get(f"/api/v1/questions/{qid}", headers=agent_headers)
    assert detail.json()["upvotes"] == 1
    assert detail.json()["score"] == 1


async def test_downvote_question(client, agent_headers, second_agent_headers):
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
        f"/api/v1/questions/{qid}/vote",
        json={
            "value": -1,
        },
        headers=second_agent_headers,
    )

    detail = await client.get(f"/api/v1/questions/{qid}", headers=agent_headers)
    assert detail.json()["downvotes"] == 1
    assert detail.json()["score"] == -1


async def test_no_double_vote(client, agent_headers, second_agent_headers):
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
        f"/api/v1/questions/{qid}/vote", json={"value": 1}, headers=second_agent_headers
    )
    resp = await client.post(
        f"/api/v1/questions/{qid}/vote", json={"value": 1}, headers=second_agent_headers
    )
    assert resp.status_code == 409


async def test_delete_vote(client, agent_headers, second_agent_headers):
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
        f"/api/v1/questions/{qid}/vote", json={"value": 1}, headers=second_agent_headers
    )
    resp = await client.delete(f"/api/v1/questions/{qid}/vote", headers=second_agent_headers)
    assert resp.status_code == 204

    detail = await client.get(f"/api/v1/questions/{qid}", headers=agent_headers)
    assert detail.json()["score"] == 0


async def test_vote_updates_author_karma(client, agent_headers, second_agent_headers):
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
        f"/api/v1/questions/{qid}/vote", json={"value": 1}, headers=second_agent_headers
    )

    me = await client.get("/api/v1/agents/me", headers=agent_headers)
    assert me.json()["question_karma"] == 1


async def test_upvote_answer(client, agent_headers, second_agent_headers):
    q = await client.post(
        "/api/v1/questions",
        json={
            "title": "Q1",
            "body": "Body",
        },
        headers=agent_headers,
    )
    qid = q.json()["id"]

    a = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={
            "body": "My answer",
        },
        headers=second_agent_headers,
    )
    aid = a.json()["id"]

    await client.post(f"/api/v1/answers/{aid}/vote", json={"value": 1}, headers=agent_headers)

    me = await client.get("/api/v1/agents/me", headers=second_agent_headers)
    assert me.json()["answer_karma"] == 1


async def test_delete_vote_reverses_karma(client, agent_headers, second_agent_headers):
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
        f"/api/v1/questions/{qid}/vote", json={"value": 1}, headers=second_agent_headers
    )
    await client.delete(f"/api/v1/questions/{qid}/vote", headers=second_agent_headers)

    me = await client.get("/api/v1/agents/me", headers=agent_headers)
    assert me.json()["question_karma"] == 0
