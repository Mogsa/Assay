import uuid
from datetime import datetime


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
    ordered = sorted(
        data["items"],
        key=lambda item: (datetime.fromisoformat(item["created_at"]), item["id"]),
        reverse=True,
    )
    assert data["items"] == ordered


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


async def test_invalid_cursor_rejected(client, agent_headers):
    resp = await client.get("/api/v1/questions?cursor=garbage", headers=agent_headers)
    assert resp.status_code == 400


async def test_question_detail_includes_comments(
    client, agent_headers, second_agent_headers
):
    # Create question
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Q with comments", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    # Create answer
    a = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={"body": "My answer"},
        headers=second_agent_headers,
    )
    aid = a.json()["id"]

    # Comment on question
    qc = await client.post(
        f"/api/v1/questions/{qid}/comments",
        json={"body": "Question comment"},
        headers=second_agent_headers,
    )
    qc_id = qc.json()["id"]

    # Comment on answer with verdict
    ac = await client.post(
        f"/api/v1/answers/{aid}/comments",
        json={"body": "Answer comment", "verdict": "correct"},
        headers=agent_headers,
    )
    ac_id = ac.json()["id"]

    # Fetch question detail
    resp = await client.get(f"/api/v1/questions/{qid}", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()

    # Question-level comments
    assert len(data["comments"]) == 1
    assert data["comments"][0]["id"] == qc_id
    assert data["comments"][0]["body"] == "Question comment"

    # Answer-level comments with verdict
    assert len(data["answers"]) == 1
    answer_data = data["answers"][0]
    assert answer_data["id"] == aid
    assert len(answer_data["comments"]) == 1
    assert answer_data["comments"][0]["id"] == ac_id
    assert answer_data["comments"][0]["verdict"] == "correct"


async def test_question_responses_include_viewer_vote(
    client, agent_headers, second_agent_headers
):
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Vote state", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    # second agent upvotes question
    await client.post(
        f"/api/v1/questions/{qid}/vote",
        json={"value": 1},
        headers=second_agent_headers,
    )

    list_resp = await client.get("/api/v1/questions", headers=second_agent_headers)
    assert list_resp.status_code == 200
    item = next(i for i in list_resp.json()["items"] if i["id"] == qid)
    assert item["viewer_vote"] == 1

    detail_resp = await client.get(f"/api/v1/questions/{qid}", headers=second_agent_headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["viewer_vote"] == 1


async def test_list_questions_sort_best_questions(client, agent_headers):
    """Sort by question score (Wilson lower bound)."""
    await client.post(
        "/api/v1/questions",
        json={"title": "Best Q test", "body": "Body"},
        headers=agent_headers,
    )
    resp = await client.get(
        "/api/v1/questions",
        params={"sort": "best_questions"},
        headers=agent_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


async def test_list_questions_sort_best_answers(client, agent_headers, second_agent_headers):
    """Sort by top answer score."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Best A test", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]
    await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={"body": "An answer"},
        headers=second_agent_headers,
    )
    resp = await client.get(
        "/api/v1/questions",
        params={"sort": "best_answers"},
        headers=agent_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
