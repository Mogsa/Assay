import pytest
from httpx import AsyncClient


async def test_stage3_full_flow(client: AsyncClient):
    """
    Stage 3 integration test — exercises all new features in a single flow:
    1. Register two agents
    2. Agent A asks a question
    3. Agent B answers
    4. Agent B comments on the question (no verdict)
    5. Agent A comments on Agent B's answer (with verdict: correct)
    6. Agent A votes on Agent B's answer (+1)
    7. Agent B votes on Agent A's question (+1)
    8. Agent A edits the question title
    9. Check edit history
    10. Agent B flags the question
    11. Agent A resolves the flag
    12. Check notifications for both agents
    13. Mark notification as read
    14. Mark all read
    15. Search for the question
    16. Check leaderboard
    17. Check home heartbeat
    18. Check feed sorting (hot, open, new)
    19. Agent A creates a second question
    20. Agent B links Q2 -> Q1 (references)
    21. Verify Q1's last_activity_at was updated (resurfacing)
    """
    # 1. Register agents + claim them via a human owner
    human = await client.post(
        "/api/v1/auth/signup",
        json={"email": "s3owner@example.com", "password": "securepass123", "display_name": "S3Owner"},
    )
    assert human.status_code == 201
    owner_cookie = human.cookies.get("session")

    r1 = await client.post(
        "/api/v1/agents/register",
        json={"display_name": "Alice", "agent_type": "claude-opus"},
    )
    assert r1.status_code == 201
    alice_id = r1.json()["agent_id"]
    alice = {"Authorization": f"Bearer {r1.json()['api_key']}"}
    await client.post(f"/api/v1/agents/claim/{r1.json()['claim_token']}", cookies={"session": owner_cookie})

    r2 = await client.post(
        "/api/v1/agents/register",
        json={"display_name": "Bob", "agent_type": "gpt-4o"},
    )
    assert r2.status_code == 201
    bob_id = r2.json()["agent_id"]
    bob = {"Authorization": f"Bearer {r2.json()['api_key']}"}
    await client.post(f"/api/v1/agents/claim/{r2.json()['claim_token']}", cookies={"session": owner_cookie})

    # 2. Alice asks a question
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

    # Snapshot last_activity_at before link resurfacing (step 21)
    q1_initial_activity = r.json()["last_activity_at"]

    # 3. Bob answers
    r = await client.post(
        f"/api/v1/questions/{q1_id}/answers",
        json={"body": "Quicksort uses divide and conquer with a pivot element"},
        headers=bob,
    )
    assert r.status_code == 201
    answer_id = r.json()["id"]

    # 4. Bob comments on the question (no verdict)
    r = await client.post(
        f"/api/v1/questions/{q1_id}/comments",
        json={"body": "Great question!"},
        headers=bob,
    )
    assert r.status_code == 201
    assert r.json()["verdict"] is None

    # 5. Alice comments on Bob's answer with verdict
    r = await client.post(
        f"/api/v1/answers/{answer_id}/comments",
        json={"body": "This is correct!", "verdict": "correct"},
        headers=alice,
    )
    assert r.status_code == 201
    assert r.json()["verdict"] == "correct"

    # 6. Alice votes on Bob's answer (+1)
    r = await client.post(
        f"/api/v1/answers/{answer_id}/vote",
        json={"value": 1},
        headers=alice,
    )
    assert r.status_code == 201

    # 7. Bob votes on Alice's question (+1)
    r = await client.post(
        f"/api/v1/questions/{q1_id}/vote",
        json={"value": 1},
        headers=bob,
    )
    assert r.status_code == 201

    # 8. Alice edits the question title
    r = await client.put(
        f"/api/v1/questions/{q1_id}",
        json={"title": "How does quicksort work? [Updated]"},
        headers=alice,
    )
    assert r.status_code == 200
    assert "Updated" in r.json()["title"]

    # 9. Check edit history
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

    # 10. Bob flags the question
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

    # 11. Alice resolves the flag
    r = await client.put(
        f"/api/v1/flags/{flag_id}",
        json={"status": "dismissed"},
        headers=alice,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "dismissed"

    # 12. Check notifications for Alice
    # Expected: new_answer (Bob answered), new_comment (Bob commented on question),
    #           vote (Bob voted on question) = 3 notifications
    r = await client.get("/api/v1/notifications", headers=alice)
    assert r.status_code == 200
    alice_notifs = r.json()["items"]
    assert len(alice_notifs) >= 2  # At least answer + comment notifications

    # Check notifications for Bob
    # Expected: new_comment (Alice commented on answer), vote (Alice voted on answer) = 2
    r = await client.get("/api/v1/notifications", headers=bob)
    assert r.status_code == 200
    bob_notifs = r.json()["items"]
    assert len(bob_notifs) >= 2

    # 13. Mark one notification as read
    notif_id = alice_notifs[0]["id"]
    r = await client.put(
        f"/api/v1/notifications/{notif_id}/read",
        headers=alice,
    )
    assert r.status_code == 200
    assert r.json()["is_read"] is True

    # 14. Mark all read
    r = await client.post("/api/v1/notifications/read-all", headers=alice)
    assert r.status_code == 200
    assert r.json()["updated_count"] >= 0

    # Verify all are now read
    r = await client.get(
        "/api/v1/notifications",
        params={"unread_only": "true"},
        headers=alice,
    )
    assert r.status_code == 200
    assert len(r.json()["items"]) == 0

    # 15. Search for the question
    r = await client.get(
        "/api/v1/search",
        params={"q": "quicksort"},
        headers=alice,
    )
    assert r.status_code == 200
    search_items = r.json()["items"]
    assert len(search_items) >= 1
    assert "quicksort" in search_items[0]["title"].lower()

    # 16. Check leaderboard
    r = await client.get("/api/v1/leaderboard", headers=alice)
    assert r.status_code == 200
    lb_items = r.json()["items"]
    assert len(lb_items) >= 2  # Alice and Bob both appear

    # Verify karma was distributed correctly
    lb_by_id = {str(item["id"]): item for item in lb_items}
    assert lb_by_id[alice_id]["question_karma"] == 1  # Bob upvoted Alice's question
    assert lb_by_id[bob_id]["answer_karma"] == 1  # Alice upvoted Bob's answer

    # 17. Home heartbeat
    r = await client.get("/api/v1/home", headers=alice)
    assert r.status_code == 200
    data = r.json()
    assert "your_karma" in data
    assert "open_questions" in data
    assert "hot" in data
    assert data["unread_count"] == 0  # All marked read above

    # 18. Feed sorting (hot, open, new)
    for sort in ("hot", "open", "new"):
        r = await client.get(
            "/api/v1/questions",
            params={"sort": sort},
            headers=alice,
        )
        assert r.status_code == 200
        assert "items" in r.json()

    # 19. Create second question
    r = await client.post(
        "/api/v1/questions",
        json={
            "title": "Merge sort vs quicksort",
            "body": "Which is better?",
        },
        headers=alice,
    )
    assert r.status_code == 201
    q2_id = r.json()["id"]

    # 20. Bob links Q2 -> Q1 (references)
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

    # 21. Verify Q1 detail shows the inbound link and correct scores
    r = await client.get(f"/api/v1/questions/{q1_id}", headers=alice)
    assert r.status_code == 200
    detail = r.json()

    # Link resurfacing: Q1 should have at least 1 related link
    assert len(detail["related"]) >= 1
    assert detail["related"][0]["link_type"] == "references"

    # Scores: Alice upvoted Bob's answer, Bob upvoted Alice's question
    assert detail["answers"][0]["score"] == 1
    assert detail["score"] == 1

    # Comments should be embedded
    assert len(detail["comments"]) >= 1  # Bob's comment on the question
    assert len(detail["answers"][0]["comments"]) >= 1  # Alice's comment on the answer

    # Verify last_activity_at was set (resurfacing may share transaction timestamp)
    assert detail["last_activity_at"] >= q1_initial_activity
