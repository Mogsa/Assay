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
    assert resp.json()["author"]["display_name"] == "TestAgent"


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
    assert "body" in data["items"][0]
    assert data["items"][0]["author"]["display_name"] == "TestAgent"


async def test_list_questions_scan_view_is_compact_and_cursor_paginated(client, agent_headers):
    for i in range(4):
        await client.post(
            "/api/v1/questions",
            json={
                "title": f"Scan {i}",
                "body": f"Body {i}",
            },
            headers=agent_headers,
        )

    first = await client.get(
        "/api/v1/questions?view=scan&limit=2",
        headers=agent_headers,
    )
    assert first.status_code == 200
    first_data = first.json()
    assert len(first_data["items"]) == 2
    assert first_data["has_more"] is True
    assert "body" not in first_data["items"][0]
    assert first_data["items"][0]["title"].startswith("Scan")

    second = await client.get(
        f"/api/v1/questions?view=scan&limit=2&cursor={first_data['next_cursor']}",
        headers=agent_headers,
    )
    assert second.status_code == 200
    second_data = second.json()
    assert len(second_data["items"]) == 2
    assert {item["id"] for item in first_data["items"]}.isdisjoint(
        {item["id"] for item in second_data["items"]}
    )


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


async def test_public_question_reads_allow_anonymous_viewer(client, agent_headers):
    create = await client.post(
        "/api/v1/questions",
        json={"title": "Public read", "body": "Body"},
        headers=agent_headers,
    )
    qid = create.json()["id"]

    list_resp = await client.get("/api/v1/questions")
    assert list_resp.status_code == 200
    assert any(item["id"] == qid for item in list_resp.json()["items"])

    scan_resp = await client.get("/api/v1/questions?view=scan")
    assert scan_resp.status_code == 200
    scan_item = next(item for item in scan_resp.json()["items"] if item["id"] == qid)
    assert "body" not in scan_item


async def test_question_preview_summarizes_problem_reviews_and_answers(
    client,
    agent_headers,
    second_agent_headers,
    third_agent_headers,
    human_session_cookie,
):
    create = await client.post(
        "/api/v1/questions",
        json={"title": "Preview me", "body": "A detailed problem body for preview testing."},
        headers=agent_headers,
    )
    qid = create.json()["id"]

    for idx in range(4):
        comment_resp = await client.post(
            f"/api/v1/questions/{qid}/comments",
            json={"body": f"Problem review {idx}"},
            headers=second_agent_headers,
        )
        assert comment_resp.status_code == 201

    answer_ids = []
    for payload, auth in [
        ({"body": "Answer one body"}, second_agent_headers),
        ({"body": "Answer two body"}, third_agent_headers),
        ({"body": "Human answer body"}, {"session": human_session_cookie}),
    ]:
        if "session" in auth:
            answer_resp = await client.post(
                f"/api/v1/questions/{qid}/answers",
                json=payload,
                cookies=auth,
            )
        else:
            answer_resp = await client.post(
                f"/api/v1/questions/{qid}/answers",
                json=payload,
                headers=auth,
            )
        assert answer_resp.status_code == 201
        answer_ids.append(answer_resp.json()["id"])

    answer_review = await client.post(
        f"/api/v1/answers/{answer_ids[0]}/comments",
        json={"body": "Top answer review", "verdict": "correct"},
        headers=agent_headers,
    )
    assert answer_review.status_code == 201

    preview = await client.get(f"/api/v1/questions/{qid}/preview")
    assert preview.status_code == 200
    data = preview.json()
    assert data["created_via"] == "manual"
    assert len(data["problem_reviews"]) == 3
    assert data["hidden_problem_review_count"] == 1
    assert len(data["answers"]) == 2
    assert data["hidden_answer_count"] == 1
    assert data["answers"][0]["top_review"]["body"] == "Top answer review"
    assert data["answers"][0]["top_review"]["created_via"] == "manual"

    detail_resp = await client.get(f"/api/v1/questions/{qid}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["author"]["display_name"] == "TestAgent"


async def test_list_questions_sort_discriminating(client, agent_headers, second_agent_headers):
    """Questions with more incorrect/partial verdicts rank higher."""
    # Q1: no verdicts
    q1 = await client.post(
        "/api/v1/questions",
        json={"title": "Easy question no verdicts", "body": "Body"},
        headers=agent_headers,
    )
    q1_id = q1.json()["id"]

    # Q2: one incorrect verdict
    q2 = await client.post(
        "/api/v1/questions",
        json={"title": "Contested question", "body": "Body"},
        headers=agent_headers,
    )
    q2_id = q2.json()["id"]
    ans2 = await client.post(
        f"/api/v1/questions/{q2_id}/answers",
        json={"body": "An answer"},
        headers=second_agent_headers,
    )
    ans2_id = ans2.json()["id"]
    await client.post(
        f"/api/v1/answers/{ans2_id}/comments",
        json={"body": "This is wrong", "verdict": "incorrect"},
        headers=agent_headers,
    )

    resp = await client.get(
        "/api/v1/questions",
        params={"sort": "discriminating"},
        headers=agent_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    ids = [item["id"] for item in data["items"]]
    assert ids.index(q2_id) < ids.index(q1_id)  # Q2 ranks before Q1
    # Q1 has no answers — it should still appear in the results (score 0)
    assert q1_id in ids


async def test_any_participant_can_change_question_status(client, agent_headers, second_agent_headers):
    """Any participant can change question status, not just the author."""
    create = await client.post(
        "/api/v1/questions",
        json={"title": "Status update", "body": "Body"},
        headers=agent_headers,
    )
    qid = create.json()["id"]

    # Non-author (second_agent) can change status
    updated = await client.put(
        f"/api/v1/questions/{qid}/status",
        json={"status": "resolved"},
        headers=second_agent_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "resolved"

    # Author can also change status
    reopened = await client.put(
        f"/api/v1/questions/{qid}/status",
        json={"status": "open"},
        headers=agent_headers,
    )
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "open"
