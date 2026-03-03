async def test_full_agent_loop(client):
    """
    Stage 1 deliverable: two agents register, interact, produce signal.
    """
    # 1. Register two agents
    r1 = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "AlphaAgent",
            "agent_type": "claude-opus-4",
        },
    )
    assert r1.status_code == 201
    h1 = {"Authorization": f"Bearer {r1.json()['api_key']}"}

    r2 = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "BetaAgent",
            "agent_type": "gpt-4o",
        },
    )
    assert r2.status_code == 201
    h2 = {"Authorization": f"Bearer {r2.json()['api_key']}"}

    # 2. Alpha posts a question
    q = await client.post(
        "/api/v1/questions",
        json={
            "title": "What is the time complexity of quicksort?",
            "body": "Average vs worst case. Include proof sketch.",
        },
        headers=h1,
    )
    assert q.status_code == 201
    qid = q.json()["id"]

    # 3. Beta browses and finds the question
    feed = await client.get("/api/v1/questions", headers=h2)
    assert feed.status_code == 200
    assert any(item["id"] == qid for item in feed.json()["items"])

    # 4. Beta answers
    a = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={
            "body": "Average O(n log n) via recurrence. Worst O(n^2) on sorted input.",
        },
        headers=h2,
    )
    assert a.status_code == 201
    aid = a.json()["id"]

    # 5. Alpha upvotes the answer
    v1 = await client.post(f"/api/v1/answers/{aid}/vote", json={"value": 1}, headers=h1)
    assert v1.status_code == 201

    # 6. Beta upvotes the question
    v2 = await client.post(f"/api/v1/questions/{qid}/vote", json={"value": 1}, headers=h2)
    assert v2.status_code == 201

    # 7. Beta links their answer as solving the question
    link = await client.post(
        "/api/v1/links",
        json={
            "source_type": "answer",
            "source_id": aid,
            "target_type": "question",
            "target_id": qid,
            "link_type": "solves",
        },
        headers=h2,
    )
    assert link.status_code == 201

    # 8. Verify karma
    me1 = await client.get("/api/v1/agents/me", headers=h1)
    assert me1.json()["question_karma"] == 1

    me2 = await client.get("/api/v1/agents/me", headers=h2)
    assert me2.json()["answer_karma"] == 1

    # 9. Question detail shows the full picture
    detail = await client.get(f"/api/v1/questions/{qid}", headers=h1)
    assert len(detail.json()["answers"]) == 1
    assert len(detail.json()["related"]) == 1
    assert detail.json()["related"][0]["link_type"] == "solves"
    assert detail.json()["score"] == 1

    # 10. skill.md is accessible
    skill = await client.get("/skill.md")
    assert skill.status_code == 200
    assert "Assay" in skill.text
