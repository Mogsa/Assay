async def _create_question(client, headers):
    resp = await client.post(
        "/api/v1/questions",
        json={"title": "Test Q", "body": "Test body"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_create_flag(client, agent_headers):
    question_id = await _create_question(client, agent_headers)

    resp = await client.post(
        "/api/v1/flags",
        json={
            "target_type": "question",
            "target_id": question_id,
            "reason": "spam",
            "detail": "This looks like spam",
        },
        headers=agent_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["target_type"] == "question"
    assert data["target_id"] == question_id
    assert data["reason"] == "spam"
    assert data["detail"] == "This looks like spam"
    assert data["status"] == "pending"


async def test_list_pending_flags(client, agent_headers):
    question_id = await _create_question(client, agent_headers)

    # Create two flags
    for reason in ("spam", "offensive"):
        await client.post(
            "/api/v1/flags",
            json={
                "target_type": "question",
                "target_id": question_id,
                "reason": reason,
            },
            headers=agent_headers,
        )

    resp = await client.get("/api/v1/flags", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["has_more"] is False
    assert data["next_cursor"] is None
    # Ordered by created_at DESC — most recent first
    assert data["items"][0]["reason"] == "offensive"
    assert data["items"][1]["reason"] == "spam"


async def test_resolve_flag(client, agent_headers, second_agent_headers):
    question_id = await _create_question(client, agent_headers)

    create_resp = await client.post(
        "/api/v1/flags",
        json={
            "target_type": "question",
            "target_id": question_id,
            "reason": "spam",
        },
        headers=agent_headers,
    )
    flag_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/flags/{flag_id}",
        json={"status": "resolved"},
        headers=second_agent_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "resolved"

    # Resolved flag should not appear in pending list
    list_resp = await client.get("/api/v1/flags", headers=agent_headers)
    assert len(list_resp.json()["items"]) == 0


async def test_dismiss_flag(client, agent_headers):
    question_id = await _create_question(client, agent_headers)

    create_resp = await client.post(
        "/api/v1/flags",
        json={
            "target_type": "question",
            "target_id": question_id,
            "reason": "off_topic",
        },
        headers=agent_headers,
    )
    flag_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/flags/{flag_id}",
        json={"status": "dismissed"},
        headers=agent_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "dismissed"


async def test_flag_requires_auth(client, agent_headers):
    question_id = await _create_question(client, agent_headers)

    resp = await client.post(
        "/api/v1/flags",
        json={
            "target_type": "question",
            "target_id": question_id,
            "reason": "spam",
        },
    )
    assert resp.status_code in (401, 403)
