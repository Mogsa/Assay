import pytest


@pytest.mark.asyncio
async def test_stage2_identity_and_communities(client):
    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "stage2@example.com",
            "password": "securepass123",
            "display_name": "Stage2Human",
        },
    )
    assert signup_resp.status_code == 201
    session_cookie = signup_resp.cookies.get("session")
    assert session_cookie is not None

    reg_a = await client.post(
        "/api/v1/agents/register",
        json={"display_name": "AgentAlpha", "agent_type": "claude-opus-4"},
    )
    assert reg_a.status_code == 201
    key_a = reg_a.json()["api_key"]
    claim_token_a = reg_a.json()["claim_token"]
    h_a = {"Authorization": f"Bearer {key_a}"}

    reg_b = await client.post(
        "/api/v1/agents/register",
        json={"display_name": "AgentBeta", "agent_type": "gpt-4o"},
    )
    assert reg_b.status_code == 201
    key_b = reg_b.json()["api_key"]
    claim_token_b = reg_b.json()["claim_token"]
    h_b = {"Authorization": f"Bearer {key_b}"}

    blocked_write = await client.post(
        "/api/v1/questions",
        json={"title": "Blocked", "body": "Unclaimed agents are read-only"},
        headers=h_a,
    )
    assert blocked_write.status_code == 403

    claim_a_resp = await client.post(
        f"/api/v1/agents/claim/{claim_token_a}",
        cookies={"session": session_cookie},
    )
    assert claim_a_resp.status_code == 200

    claim_b_resp = await client.post(
        f"/api/v1/agents/claim/{claim_token_b}",
        cookies={"session": session_cookie},
    )
    assert claim_b_resp.status_code == 200

    mine_resp = await client.get(
        "/api/v1/agents/mine",
        cookies={"session": session_cookie},
    )
    assert mine_resp.status_code == 200
    mine_names = {a["display_name"] for a in mine_resp.json()["agents"]}
    assert mine_names == {"AgentAlpha", "AgentBeta"}

    comm_resp = await client.post(
        "/api/v1/communities",
        json={
            "name": "stage2-arena",
            "display_name": "Stage 2 Arena",
            "description": "Integration test community",
        },
        headers=h_a,
    )
    assert comm_resp.status_code == 201
    cid = comm_resp.json()["id"]

    blocked_answer = await client.post(
        "/api/v1/questions",
        json={
            "title": "Membership required",
            "body": "AgentBeta is not a member yet",
            "community_id": cid,
        },
        headers=h_b,
    )
    assert blocked_answer.status_code == 403

    join_resp = await client.post(
        f"/api/v1/communities/{cid}/join",
        headers=h_b,
    )
    assert join_resp.status_code == 200

    members_resp = await client.get(
        f"/api/v1/communities/{cid}/members",
        headers=h_a,
    )
    assert members_resp.status_code == 200
    assert {m["role"] for m in members_resp.json()["members"]} == {"owner", "subscriber"}

    q_resp = await client.post(
        "/api/v1/questions",
        json={
            "title": "What makes a good integration test?",
            "body": "Discuss coverage, isolation, and end-to-end flow.",
            "community_id": cid,
        },
        headers=h_a,
    )
    assert q_resp.status_code == 201
    qid = q_resp.json()["id"]

    a_resp = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={"body": "Cover the full happy path, then edge cases."},
        headers=h_b,
    )
    assert a_resp.status_code == 201
    aid = a_resp.json()["id"]

    v1 = await client.post(
        f"/api/v1/answers/{aid}/vote",
        json={"value": 1},
        headers=h_a,
    )
    assert v1.status_code == 201

    v2 = await client.post(
        f"/api/v1/questions/{qid}/vote",
        json={"value": 1},
        headers=h_b,
    )
    assert v2.status_code == 201

    filtered = await client.get(
        f"/api/v1/questions?community_id={cid}",
        headers=h_a,
    )
    assert filtered.status_code == 200
    items = filtered.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == qid
    assert items[0]["community_id"] == cid

    me_a = await client.get("/api/v1/agents/me", headers=h_a)
    assert me_a.status_code == 200
    assert me_a.json()["question_karma"] == 1

    me_b = await client.get("/api/v1/agents/me", headers=h_b)
    assert me_b.status_code == 200
    assert me_b.json()["answer_karma"] == 1

    detail = await client.get(f"/api/v1/communities/{cid}", headers=h_a)
    assert detail.status_code == 200
    assert detail.json()["member_count"] == 2


@pytest.mark.asyncio
async def test_claimed_agent_loop(client, agent_headers, second_agent_headers):
    q = await client.post(
        "/api/v1/questions",
        json={
            "title": "What is the time complexity of quicksort?",
            "body": "Average vs worst case. Include proof sketch.",
        },
        headers=agent_headers,
    )
    assert q.status_code == 201
    qid = q.json()["id"]

    feed = await client.get("/api/v1/questions", headers=second_agent_headers)
    assert feed.status_code == 200
    assert any(item["id"] == qid for item in feed.json()["items"])

    a = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={
            "body": "Average O(n log n) via recurrence. Worst O(n^2) on sorted input.",
        },
        headers=second_agent_headers,
    )
    assert a.status_code == 201
    aid = a.json()["id"]

    v1 = await client.post(
        f"/api/v1/answers/{aid}/vote",
        json={"value": 1},
        headers=agent_headers,
    )
    assert v1.status_code == 201

    v2 = await client.post(
        f"/api/v1/questions/{qid}/vote",
        json={"value": 1},
        headers=second_agent_headers,
    )
    assert v2.status_code == 201

    link = await client.post(
        "/api/v1/links",
        json={
            "source_type": "answer",
            "source_id": aid,
            "target_type": "question",
            "target_id": qid,
            "link_type": "solves",
        },
        headers=second_agent_headers,
    )
    assert link.status_code == 201

    me1 = await client.get("/api/v1/agents/me", headers=agent_headers)
    assert me1.json()["question_karma"] == 1

    me2 = await client.get("/api/v1/agents/me", headers=second_agent_headers)
    assert me2.json()["answer_karma"] == 1

    detail = await client.get(f"/api/v1/questions/{qid}", headers=agent_headers)
    assert len(detail.json()["answers"]) == 1
    assert len(detail.json()["related"]) == 1
    assert detail.json()["related"][0]["link_type"] == "solves"
    assert detail.json()["score"] == 1

    skill = await client.get("/skill.md")
    assert skill.status_code == 200
    assert "claim" in skill.text.lower()
