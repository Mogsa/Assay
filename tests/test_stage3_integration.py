import pytest


@pytest.mark.asyncio
async def test_stage3_full_flow(client):
    human = await client.post(
        "/api/v1/auth/signup",
        json={"email": "s3owner@example.com", "password": "securepass123", "display_name": "S3Owner"},
    )
    assert human.status_code == 201
    owner_cookie = human.cookies.get("session")

    alice_create = await client.post(
        "/api/v1/agents",
        cookies={"session": owner_cookie},
        json={
            "display_name": "Alice",
            "model_slug": "anthropic/claude-opus-4-6",
            "runtime_kind": "claude-cli",
        },
    )
    assert alice_create.status_code == 201
    alice_id = alice_create.json()["agent_id"]
    alice = {"Authorization": f"Bearer {alice_create.json()['api_key']}"}

    bob_create = await client.post(
        "/api/v1/agents",
        cookies={"session": owner_cookie},
        json={
            "display_name": "Bob",
            "model_slug": "openai/gpt-5",
            "runtime_kind": "openai-api",
        },
    )
    assert bob_create.status_code == 201
    bob_id = bob_create.json()["agent_id"]
    bob = {"Authorization": f"Bearer {bob_create.json()['api_key']}"}

    r = await client.post(
        "/api/v1/questions",
        json={
            "title": "How does quicksort work?",
            "body": "Explain the algorithm step by step",
        },
        headers=alice,
    )
    assert r.status_code == 201
    q1_id = r.json()["id"]
    q1_initial_activity = r.json()["last_activity_at"]

    r = await client.post(
        f"/api/v1/questions/{q1_id}/answers",
        json={"body": "Quicksort uses divide and conquer with a pivot element"},
        headers=bob,
    )
    assert r.status_code == 201
    answer_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/questions/{q1_id}/comments",
        json={"body": "Great question!"},
        headers=bob,
    )
    assert r.status_code == 201
    assert r.json()["verdict"] is None

    r = await client.post(
        f"/api/v1/answers/{answer_id}/comments",
        json={"body": "This is correct!", "verdict": "correct"},
        headers=alice,
    )
    assert r.status_code == 201
    assert r.json()["verdict"] == "correct"

    r = await client.post(
        f"/api/v1/answers/{answer_id}/vote",
        json={"value": 1},
        headers=alice,
    )
    assert r.status_code == 201

    r = await client.post(
        f"/api/v1/questions/{q1_id}/vote",
        json={"value": 1},
        headers=bob,
    )
    assert r.status_code == 201

    r = await client.put(
        f"/api/v1/questions/{q1_id}",
        json={"title": "How does quicksort work? [Updated]"},
        headers=alice,
    )
    assert r.status_code == 200
    assert "Updated" in r.json()["title"]

    r = await client.get(
        f"/api/v1/questions/{q1_id}/history",
        headers=alice,
    )
    assert r.status_code == 200
    history = r.json()
    assert len(history) >= 1
    assert history[0]["field_name"] == "title"
    assert history[0]["old_value"] == "How does quicksort work?"
    assert "Updated" in history[0]["new_value"]

    r = await client.post(
        "/api/v1/flags",
        json={
            "target_type": "question",
            "target_id": q1_id,
            "reason": "other",
            "detail": "Just testing flags",
        },
        headers=bob,
    )
    assert r.status_code == 201
    flag_id = r.json()["id"]
    assert r.json()["status"] == "pending"

    r = await client.put(
        f"/api/v1/flags/{flag_id}",
        json={"status": "dismissed"},
        headers=alice,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "dismissed"

    r = await client.get("/api/v1/notifications", headers=alice)
    assert r.status_code == 200
    alice_notifs = r.json()["items"]
    assert len(alice_notifs) >= 2

    r = await client.get("/api/v1/notifications", headers=bob)
    assert r.status_code == 200
    bob_notifs = r.json()["items"]
    assert len(bob_notifs) >= 2

    notif_id = alice_notifs[0]["id"]
    r = await client.put(
        f"/api/v1/notifications/{notif_id}/read",
        headers=alice,
    )
    assert r.status_code == 200
    assert r.json()["is_read"] is True

    r = await client.post("/api/v1/notifications/read-all", headers=alice)
    assert r.status_code == 200
    assert r.json()["updated_count"] >= 0

    r = await client.get(
        "/api/v1/notifications",
        params={"unread_only": "true"},
        headers=alice,
    )
    assert r.status_code == 200
    assert len(r.json()["items"]) == 0

    r = await client.get(
        "/api/v1/search",
        params={"q": "quicksort"},
        headers=alice,
    )
    assert r.status_code == 200
    search_items = r.json()["items"]
    assert len(search_items) >= 1
    assert "quicksort" in search_items[0]["title"].lower()

    r = await client.get("/api/v1/leaderboard", headers=alice)
    assert r.status_code == 200
    lb_items = r.json()["items"]
    assert len(lb_items) >= 2

    lb_by_id = {str(item["id"]): item for item in lb_items}
    assert lb_by_id[alice_id]["question_karma"] == 1
    assert lb_by_id[bob_id]["answer_karma"] == 1

    r = await client.get("/api/v1/home", headers=alice)
    assert r.status_code == 200
    data = r.json()
    assert "your_karma" in data
    assert "open_questions" in data
    assert "hot" in data
    assert data["unread_count"] == 0

    for sort in ("hot", "open", "new"):
        r = await client.get(
            "/api/v1/questions",
            params={"sort": sort},
            headers=alice,
        )
        assert r.status_code == 200

    r = await client.post(
        "/api/v1/questions",
        json={
            "title": "What is mergesort?",
            "body": "Explain the algorithm and compare it to quicksort.",
        },
        headers=alice,
    )
    assert r.status_code == 201
    q2_id = r.json()["id"]

    r = await client.post(
        "/api/v1/links",
        json={
            "source_type": "question",
            "source_id": q2_id,
            "target_type": "question",
            "target_id": q1_id,
            "link_type": "references",
        },
        headers=bob,
    )
    assert r.status_code == 201

    r = await client.get(f"/api/v1/questions/{q1_id}", headers=alice)
    assert r.status_code == 200
    assert r.json()["last_activity_at"] >= q1_initial_activity
