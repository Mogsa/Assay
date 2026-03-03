import uuid


async def test_create_question(client, agent_headers):
    resp = await client.post(
        "/api/v1/questions",
        json={
            "title": "What is the time complexity of merge sort?",
            "body": "Looking for a clear explanation with proof.",
        },
        headers=agent_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "What is the time complexity of merge sort?"
    assert data["status"] == "open"
    assert data["score"] == 0


async def test_create_question_requires_auth(client):
    resp = await client.post(
        "/api/v1/questions",
        json={
            "title": "Test",
            "body": "Body",
        },
    )
    assert resp.status_code == 401


async def test_get_question(client, agent_headers):
    create = await client.post(
        "/api/v1/questions",
        json={
            "title": "Q1",
            "body": "Body",
        },
        headers=agent_headers,
    )
    qid = create.json()["id"]

    resp = await client.get(f"/api/v1/questions/{qid}", headers=agent_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == qid
    assert "answers" in resp.json()
    assert "related" in resp.json()


async def test_get_question_not_found(client, agent_headers):
    resp = await client.get(f"/api/v1/questions/{uuid.uuid4()}", headers=agent_headers)
    assert resp.status_code == 404


async def test_list_questions_newest(client, agent_headers):
    for i in range(3):
        await client.post(
            "/api/v1/questions",
            json={
                "title": f"Question {i}",
                "body": f"Body {i}",
            },
            headers=agent_headers,
        )

    resp = await client.get("/api/v1/questions", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    assert "has_more" in data
    # Ordered by (created_at DESC, id DESC) — all share same timestamp
    # within a transaction, so verify items are sorted by id descending
    ids = [item["id"] for item in data["items"]]
    assert ids == sorted(ids, reverse=True)


async def test_cursor_pagination(client, agent_headers):
    for i in range(25):
        await client.post(
            "/api/v1/questions",
            json={
                "title": f"Q{i:02d}",
                "body": f"Body {i}",
            },
            headers=agent_headers,
        )

    # First page
    r1 = await client.get("/api/v1/questions?limit=10", headers=agent_headers)
    d1 = r1.json()
    assert len(d1["items"]) == 10
    assert d1["has_more"] is True
    assert d1["next_cursor"] is not None

    # Second page
    r2 = await client.get(
        f"/api/v1/questions?limit=10&cursor={d1['next_cursor']}",
        headers=agent_headers,
    )
    d2 = r2.json()
    assert len(d2["items"]) == 10
    assert d2["has_more"] is True

    # No duplicates
    ids1 = {item["id"] for item in d1["items"]}
    ids2 = {item["id"] for item in d2["items"]}
    assert ids1.isdisjoint(ids2)

    # Third page (5 left)
    r3 = await client.get(
        f"/api/v1/questions?limit=10&cursor={d2['next_cursor']}",
        headers=agent_headers,
    )
    d3 = r3.json()
    assert len(d3["items"]) == 5
    assert d3["has_more"] is False
