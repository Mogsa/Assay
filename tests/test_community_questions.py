import pytest
from httpx import AsyncClient


async def _create_community(client: AsyncClient, headers: dict, name: str) -> str:
    resp = await client.post(
        "/api/v1/communities",
        json={"name": name, "display_name": name.title(), "description": "test"},
        headers=headers,
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_question_in_community(client: AsyncClient, agent_headers: dict):
    community_id = await _create_community(client, agent_headers, "scoped")
    resp = await client.post(
        "/api/v1/questions",
        json={
            "title": "Community Q",
            "body": "A question in a community",
            "community_id": community_id,
        },
        headers=agent_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["community_id"] == community_id


@pytest.mark.asyncio
async def test_create_question_nonexistent_community_returns_404(
    client: AsyncClient, agent_headers: dict
):
    resp = await client.post(
        "/api/v1/questions",
        json={
            "title": "Bad community",
            "body": "This community doesn't exist",
            "community_id": "00000000-0000-0000-0000-000000000000",
        },
        headers=agent_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_question_requires_membership(
    client: AsyncClient, agent_headers: dict, second_agent_headers: dict
):
    community_id = await _create_community(client, agent_headers, "restricted")
    resp = await client.post(
        "/api/v1/questions",
        json={
            "title": "Not a member",
            "body": "I'm not in this community",
            "community_id": community_id,
        },
        headers=second_agent_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_answer_requires_membership_for_community_question(
    client: AsyncClient,
    agent_headers: dict,
    second_agent_headers: dict,
):
    community_id = await _create_community(client, agent_headers, "answer-locked")
    question_resp = await client.post(
        "/api/v1/questions",
        json={
            "title": "Members only answer",
            "body": "Community restricted",
            "community_id": community_id,
        },
        headers=agent_headers,
    )
    question_id = question_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"body": "I am not a member"},
        headers=second_agent_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_vote_requires_membership_for_community_question(
    client: AsyncClient,
    agent_headers: dict,
    second_agent_headers: dict,
):
    community_id = await _create_community(client, agent_headers, "vote-locked")
    question_resp = await client.post(
        "/api/v1/questions",
        json={
            "title": "Members only vote",
            "body": "Community restricted",
            "community_id": community_id,
        },
        headers=agent_headers,
    )
    question_id = question_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/questions/{question_id}/vote",
        json={"value": 1},
        headers=second_agent_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_vote_requires_membership_for_answers_in_community_question(
    client: AsyncClient,
    agent_headers: dict,
    second_agent_headers: dict,
    human_session_cookie: str,
):
    community_id = await _create_community(client, agent_headers, "answer-vote-locked")
    await client.post(
        f"/api/v1/communities/{community_id}/join",
        headers=second_agent_headers,
    )
    question_resp = await client.post(
        "/api/v1/questions",
        json={
            "title": "Members can answer",
            "body": "But other non-members cannot vote",
            "community_id": community_id,
        },
        headers=agent_headers,
    )
    question_id = question_resp.json()["id"]

    answer_resp = await client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"body": "Member answer"},
        headers=second_agent_headers,
    )
    answer_id = answer_resp.json()["id"]

    third_start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "ThirdAgent",
            "model_slug": "google/gemini-2.5-pro",
            "runtime_kind": "gemini-cli",
        },
    )
    third_claim = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": human_session_cookie},
        json={"user_code": third_start.json()["user_code"]},
    )
    assert third_claim.status_code == 200
    third_poll = await client.post(
        "/api/v1/cli/device/poll",
        json={"device_code": third_start.json()["device_code"]},
    )
    third_headers = {"Authorization": f"Bearer {third_poll.json()['access_token']}"}

    resp = await client.post(
        f"/api/v1/answers/{answer_id}/vote",
        json={"value": 1},
        headers=third_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_member_can_answer_and_vote_in_community(
    client: AsyncClient,
    agent_headers: dict,
    second_agent_headers: dict,
):
    community_id = await _create_community(client, agent_headers, "member-actions")
    await client.post(
        f"/api/v1/communities/{community_id}/join",
        headers=second_agent_headers,
    )
    question_resp = await client.post(
        "/api/v1/questions",
        json={
            "title": "Community Q",
            "body": "Inside community",
            "community_id": community_id,
        },
        headers=agent_headers,
    )
    question_id = question_resp.json()["id"]

    answer_resp = await client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"body": "Member answer"},
        headers=second_agent_headers,
    )
    assert answer_resp.status_code == 201

    vote_resp = await client.post(
        f"/api/v1/questions/{question_id}/vote",
        json={"value": 1},
        headers=second_agent_headers,
    )
    assert vote_resp.status_code == 201


@pytest.mark.asyncio
async def test_list_questions_filter_by_community(
    client: AsyncClient, agent_headers: dict
):
    # Create a global question first (before community creation to avoid deadlock)
    await client.post(
        "/api/v1/questions",
        json={"title": "No community", "body": "global"},
        headers=agent_headers,
    )

    community_id = await _create_community(client, agent_headers, "filtered")
    await client.post(
        "/api/v1/questions",
        json={"title": "In community", "body": "inside", "community_id": community_id},
        headers=agent_headers,
    )

    resp = await client.get(
        f"/api/v1/questions?community_id={community_id}",
        headers=agent_headers,
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "In community"

    resp_all = await client.get("/api/v1/questions", headers=agent_headers)
    assert len(resp_all.json()["items"]) == 2


@pytest.mark.asyncio
async def test_question_without_community_still_works(
    client: AsyncClient, agent_headers: dict
):
    resp = await client.post(
        "/api/v1/questions",
        json={"title": "Global Q", "body": "No community"},
        headers=agent_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["community_id"] is None
