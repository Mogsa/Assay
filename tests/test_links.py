async def test_create_link(client, agent_headers):
    q1 = await client.post("/api/v1/questions", json={
        "title": "Q1", "body": "Body 1",
    }, headers=agent_headers)
    q2 = await client.post("/api/v1/questions", json={
        "title": "Q2", "body": "Body 2",
    }, headers=agent_headers)

    resp = await client.post("/api/v1/links", json={
        "source_type": "question",
        "source_id": q2.json()["id"],
        "target_type": "question",
        "target_id": q1.json()["id"],
        "link_type": "references",
    }, headers=agent_headers)
    assert resp.status_code == 201


async def test_link_appears_in_question_detail(client, agent_headers):
    q1 = await client.post("/api/v1/questions", json={
        "title": "Original", "body": "Body",
    }, headers=agent_headers)
    q2 = await client.post("/api/v1/questions", json={
        "title": "Follow-up", "body": "Body",
    }, headers=agent_headers)

    await client.post("/api/v1/links", json={
        "source_type": "question",
        "source_id": q2.json()["id"],
        "target_type": "question",
        "target_id": q1.json()["id"],
        "link_type": "extends",
    }, headers=agent_headers)

    detail = await client.get(
        f"/api/v1/questions/{q1.json()['id']}", headers=agent_headers
    )
    assert len(detail.json()["related"]) == 1
    assert detail.json()["related"][0]["link_type"] == "extends"


async def test_answer_contradicts_answer(client, agent_headers, second_agent_headers):
    q = await client.post("/api/v1/questions", json={
        "title": "Q1", "body": "Body",
    }, headers=agent_headers)
    qid = q.json()["id"]

    a1 = await client.post(f"/api/v1/questions/{qid}/answers", json={
        "body": "Answer A",
    }, headers=agent_headers)
    a2 = await client.post(f"/api/v1/questions/{qid}/answers", json={
        "body": "Answer B",
    }, headers=second_agent_headers)

    resp = await client.post("/api/v1/links", json={
        "source_type": "answer",
        "source_id": a2.json()["id"],
        "target_type": "answer",
        "target_id": a1.json()["id"],
        "link_type": "contradicts",
    }, headers=second_agent_headers)
    assert resp.status_code == 201


async def test_duplicate_link_rejected(client, agent_headers):
    q1 = await client.post("/api/v1/questions", json={
        "title": "Q1", "body": "B1",
    }, headers=agent_headers)
    q2 = await client.post("/api/v1/questions", json={
        "title": "Q2", "body": "B2",
    }, headers=agent_headers)

    link_data = {
        "source_type": "question",
        "source_id": q2.json()["id"],
        "target_type": "question",
        "target_id": q1.json()["id"],
        "link_type": "references",
    }
    await client.post("/api/v1/links", json=link_data, headers=agent_headers)
    resp = await client.post("/api/v1/links", json=link_data, headers=agent_headers)
    assert resp.status_code == 409


async def test_link_type_validation(client, agent_headers):
    q = await client.post("/api/v1/questions", json={
        "title": "Q1", "body": "Body",
    }, headers=agent_headers)
    resp = await client.post("/api/v1/links", json={
        "source_type": "question",
        "source_id": q.json()["id"],
        "target_type": "question",
        "target_id": q.json()["id"],
        "link_type": "invalid_type",
    }, headers=agent_headers)
    assert resp.status_code == 422
