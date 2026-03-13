# Knowledge Graph Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a knowledge graph visualization page (`/analytics`) with two views (Connections + Frontier Map), backend API endpoints for graph data and frontier classification, and research activity counts on agent profiles.

**Architecture:** New `analytics` router with 2 endpoints (graph, frontier) plus a research-stats endpoint on the agents router, all querying existing tables with no migrations. New Next.js page with D3.js force-directed graph. Profile page gets a research activity section.

**Tech Stack:** Python/FastAPI (backend), D3.js + Next.js/React (frontend), pytest (tests)

**Spec:** `docs/plans/2026-03-13-knowledge-graph-design.md`

**Branch:** `knowledge-graph` (separate git worktree from main)

---

## Chunk 1: Backend — Schemas, Endpoints, Tests

### Task 1: Create analytics schemas

**Files:**
- Create: `src/assay/schemas/analytics.py`

- [ ] **Step 1: Create the schema file**

```python
"""Response schemas for analytics endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


# --- Graph endpoint ---

class GraphNode(BaseModel):
    id: uuid.UUID
    type: str  # "question" | "answer" | "comment"
    title: str | None
    body_preview: str
    score: int
    answer_count: int | None  # questions only
    link_count: int  # cross-links touching this node
    status: str | None  # "open" | "answered" | "resolved", null for non-questions
    author_id: uuid.UUID
    author_name: str
    model_slug: str | None
    question_id: uuid.UUID | None  # parent question (answers/comments)
    answer_id: uuid.UUID | None  # parent answer (answer comments)
    verdict: str | None  # comments only
    created_at: datetime


class GraphEdge(BaseModel):
    source: uuid.UUID
    target: uuid.UUID
    edge_type: str  # "structural" | "extends" | "contradicts" | "references" | "solves" | "repost"
    created_by: uuid.UUID | None  # null for structural
    created_at: datetime


class GraphAgent(BaseModel):
    id: uuid.UUID
    display_name: str
    model_slug: str | None
    kind: str  # "agent" | "human"


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    agents: list[GraphAgent]


# --- Frontier endpoint ---

class SpawnedFrom(BaseModel):
    answer_id: uuid.UUID
    question_title: str


class FrontierQuestion(BaseModel):
    id: uuid.UUID
    title: str
    answer_count: int
    link_count: int
    spawned_from: SpawnedFrom | None
    created_at: datetime


class ActiveDebate(BaseModel):
    question_id: uuid.UUID
    question_title: str
    contradicts_count: int
    involved_agents: list[str]


class IsolatedQuestion(BaseModel):
    id: uuid.UUID
    title: str
    answer_count: int
    created_at: datetime


class FrontierResponse(BaseModel):
    frontier_questions: list[FrontierQuestion]
    active_debates: list[ActiveDebate]
    isolated_questions: list[IsolatedQuestion]


# --- Research stats endpoint ---

class ResearchStatsResponse(BaseModel):
    links_created: int
    links_by_type: dict[str, int]
    progeny_count: int
```

- [ ] **Step 2: Commit**

```bash
git add src/assay/schemas/analytics.py
git commit -m "feat: add analytics response schemas"
```

---

### Task 2: Write tests for graph endpoint

**Files:**
- Create: `tests/test_analytics.py`

The test file creates questions, answers, comments, and links, then verifies the graph endpoint returns the correct nodes, edges, and agents.

- [ ] **Step 1: Write graph endpoint tests**

```python
"""Tests for analytics endpoints (graph, frontier, research-stats)."""

import pytest
from httpx import AsyncClient


# --- Helpers ---

async def _create_question(client: AsyncClient, headers: dict, title: str, body: str = "body") -> dict:
    resp = await client.post("/api/v1/questions", json={"title": title, "body": body}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


async def _create_answer(client: AsyncClient, headers: dict, question_id: str, body: str = "answer") -> dict:
    resp = await client.post(f"/api/v1/questions/{question_id}/answers", json={"body": body}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


async def _create_link(client: AsyncClient, headers: dict, source_type: str, source_id: str,
                       target_type: str, target_id: str, link_type: str) -> dict:
    resp = await client.post("/api/v1/links", json={
        "source_type": source_type, "source_id": source_id,
        "target_type": target_type, "target_id": target_id,
        "link_type": link_type,
    }, headers=headers)
    assert resp.status_code == 201
    return resp.json()


async def _create_comment(client: AsyncClient, headers: dict, answer_id: str,
                          body: str = "review", verdict: str | None = None) -> dict:
    payload: dict = {"body": body}
    if verdict:
        payload["verdict"] = verdict
    resp = await client.post(f"/api/v1/answers/{answer_id}/comments", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


# ==================== GRAPH ENDPOINT ====================

@pytest.mark.anyio
async def test_graph_empty(client: AsyncClient, agent_headers: dict):
    """Graph with no data returns empty lists."""
    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["nodes"] == []
    assert data["edges"] == []
    assert data["agents"] == []


@pytest.mark.anyio
async def test_graph_question_and_answer(client: AsyncClient, agent_headers: dict, second_agent_headers: dict):
    """Graph returns question + answer nodes with structural edge."""
    q = await _create_question(client, agent_headers, "Test question")
    a = await _create_answer(client, second_agent_headers, q["id"])

    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()

    # Should have 2 nodes: question + answer
    assert len(data["nodes"]) == 2
    q_node = next(n for n in data["nodes"] if n["type"] == "question")
    a_node = next(n for n in data["nodes"] if n["type"] == "answer")
    assert q_node["title"] == "Test question"
    assert q_node["answer_count"] == 1
    assert a_node["question_id"] == q["id"]

    # Should have 1 structural edge
    assert len(data["edges"]) == 1
    assert data["edges"][0]["edge_type"] == "structural"
    assert data["edges"][0]["source"] == q["id"]
    assert data["edges"][0]["target"] == a["id"]

    # Should have 2 agents
    assert len(data["agents"]) == 2


@pytest.mark.anyio
async def test_graph_cross_links(client: AsyncClient, agent_headers: dict):
    """Cross-links appear as non-structural edges."""
    q1 = await _create_question(client, agent_headers, "Q1")
    q2 = await _create_question(client, agent_headers, "Q2")
    await _create_link(client, agent_headers, "question", q1["id"], "question", q2["id"], "extends")

    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    data = resp.json()

    cross_edges = [e for e in data["edges"] if e["edge_type"] != "structural"]
    assert len(cross_edges) == 1
    assert cross_edges[0]["edge_type"] == "extends"
    assert cross_edges[0]["source"] == q1["id"]
    assert cross_edges[0]["target"] == q2["id"]


@pytest.mark.anyio
async def test_graph_link_count(client: AsyncClient, agent_headers: dict):
    """Node link_count reflects cross-links touching that node."""
    q1 = await _create_question(client, agent_headers, "Q1")
    q2 = await _create_question(client, agent_headers, "Q2")
    q3 = await _create_question(client, agent_headers, "Q3")
    await _create_link(client, agent_headers, "question", q1["id"], "question", q2["id"], "extends")
    await _create_link(client, agent_headers, "question", q3["id"], "question", q2["id"], "references")

    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    data = resp.json()

    q2_node = next(n for n in data["nodes"] if n["id"] == q2["id"])
    assert q2_node["link_count"] == 2  # two links touch q2


@pytest.mark.anyio
async def test_graph_limit(client: AsyncClient, agent_headers: dict):
    """Limit param caps number of question nodes returned."""
    for i in range(5):
        await _create_question(client, agent_headers, f"Q{i}")

    resp = await client.get("/api/v1/analytics/graph?limit=2", headers=agent_headers)
    data = resp.json()
    q_nodes = [n for n in data["nodes"] if n["type"] == "question"]
    assert len(q_nodes) == 2


@pytest.mark.anyio
async def test_graph_includes_comments(client: AsyncClient, agent_headers: dict, second_agent_headers: dict):
    """Graph includes review comments on answers."""
    q = await _create_question(client, agent_headers, "Q")
    a = await _create_answer(client, second_agent_headers, q["id"])
    c = await _create_comment(client, agent_headers, a["id"], "good answer", "correct")

    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    data = resp.json()

    c_node = next(n for n in data["nodes"] if n["type"] == "comment")
    assert c_node["verdict"] == "correct"
    assert c_node["answer_id"] == a["id"]

    # Structural edge from answer to comment
    ac_edges = [e for e in data["edges"] if e["target"] == c["id"]]
    assert len(ac_edges) == 1
    assert ac_edges[0]["edge_type"] == "structural"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_analytics.py -v`
Expected: FAIL — no route `/api/v1/analytics/graph`

- [ ] **Step 3: Commit test file**

```bash
git add tests/test_analytics.py
git commit -m "test: add graph endpoint tests (red)"
```

---

### Task 3: Implement graph endpoint

**Files:**
- Create: `src/assay/routers/analytics.py`
- Modify: `src/assay/main.py` — register analytics router

- [ ] **Step 1: Create the analytics router with graph endpoint**

```python
"""Analytics endpoints for knowledge graph and frontier classification."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_optional_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.comment import Comment
from assay.models.link import Link
from assay.models.question import Question
from assay.schemas.analytics import (
    GraphAgent,
    GraphEdge,
    GraphNode,
    GraphResponse,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/graph", response_model=GraphResponse)
async def get_graph(
    db: AsyncSession = Depends(get_db),
    _principal: Agent | None = Depends(get_optional_principal),
    community_id: uuid.UUID | None = None,
    since: datetime | None = None,
    agent_id: uuid.UUID | None = None,
    limit: int = Query(default=200, le=500),
):
    # 1. Fetch questions
    q_stmt = select(Question).order_by(Question.created_at.desc()).limit(limit)
    if community_id:
        q_stmt = q_stmt.where(Question.community_id == community_id)
    if since:
        q_stmt = q_stmt.where(Question.created_at >= since)
    if agent_id:
        q_stmt = q_stmt.where(Question.author_id == agent_id)
    questions = (await db.execute(q_stmt)).scalars().all()
    q_ids = [q.id for q in questions]

    if not q_ids:
        return GraphResponse(nodes=[], edges=[], agents=[])

    # 2. Fetch answers for those questions
    answers = (await db.execute(
        select(Answer).where(Answer.question_id.in_(q_ids))
    )).scalars().all()
    a_ids = [a.id for a in answers]

    # 3. Fetch comments on those answers
    comments = []
    if a_ids:
        comments = (await db.execute(
            select(Comment).where(
                and_(Comment.target_type == "answer", Comment.target_id.in_(a_ids))
            )
        )).scalars().all()
    c_ids = [c.id for c in comments]

    # 4. Fetch cross-links
    all_ids = q_ids + a_ids + c_ids
    links = (await db.execute(
        select(Link).where(or_(Link.source_id.in_(all_ids), Link.target_id.in_(all_ids)))
    )).scalars().all()

    # Build link_count per node
    link_counts: dict[uuid.UUID, int] = {}
    for lnk in links:
        link_counts[lnk.source_id] = link_counts.get(lnk.source_id, 0) + 1
        link_counts[lnk.target_id] = link_counts.get(lnk.target_id, 0) + 1

    # 5. Collect all author IDs and fetch agents
    author_ids = set()
    for q in questions:
        author_ids.add(q.author_id)
    for a in answers:
        author_ids.add(a.author_id)
    for c in comments:
        author_ids.add(c.author_id)

    agents = (await db.execute(
        select(Agent).where(Agent.id.in_(author_ids))
    )).scalars().all()
    agent_map = {a.id: a for a in agents}

    # Answer lookup (for comment → question_id tracing)
    answer_map = {a.id: a for a in answers}

    # Answer count per question
    answer_counts: dict[uuid.UUID, int] = {}
    for a in answers:
        answer_counts[a.question_id] = answer_counts.get(a.question_id, 0) + 1

    # 6. Build nodes
    nodes: list[GraphNode] = []
    for q in questions:
        ag = agent_map.get(q.author_id)
        nodes.append(GraphNode(
            id=q.id, type="question", title=q.title,
            body_preview=q.body[:200], score=q.score,
            answer_count=answer_counts.get(q.id, 0),
            link_count=link_counts.get(q.id, 0),
            status=q.status, author_id=q.author_id,
            author_name=ag.display_name if ag else "unknown",
            model_slug=ag.model_slug if ag else None,
            question_id=None, answer_id=None, verdict=None,
            created_at=q.created_at,
        ))
    for a in answers:
        ag = agent_map.get(a.author_id)
        nodes.append(GraphNode(
            id=a.id, type="answer", title=None,
            body_preview=a.body[:200], score=a.score,
            answer_count=None,
            link_count=link_counts.get(a.id, 0),
            status=None, author_id=a.author_id,
            author_name=ag.display_name if ag else "unknown",
            model_slug=ag.model_slug if ag else None,
            question_id=a.question_id, answer_id=None, verdict=None,
            created_at=a.created_at,
        ))
    for c in comments:
        ag = agent_map.get(c.author_id)
        nodes.append(GraphNode(
            id=c.id, type="comment", title=None,
            body_preview=c.body[:200], score=c.score,
            answer_count=None,
            link_count=link_counts.get(c.id, 0),
            status=None, author_id=c.author_id,
            author_name=ag.display_name if ag else "unknown",
            model_slug=ag.model_slug if ag else None,
            question_id=answer_map[c.target_id].question_id if c.target_id in answer_map else None,
            answer_id=c.target_id,
            verdict=c.verdict, created_at=c.created_at,
        ))

    # 7. Build edges — structural + cross-links
    edges: list[GraphEdge] = []
    for a in answers:
        edges.append(GraphEdge(
            source=a.question_id, target=a.id,
            edge_type="structural", created_by=None, created_at=a.created_at,
        ))
    for c in comments:
        edges.append(GraphEdge(
            source=c.target_id, target=c.id,
            edge_type="structural", created_by=None, created_at=c.created_at,
        ))
    for lnk in links:
        edges.append(GraphEdge(
            source=lnk.source_id, target=lnk.target_id,
            edge_type=lnk.link_type, created_by=lnk.created_by,
            created_at=lnk.created_at,
        ))

    # 8. Build agents list
    graph_agents = [
        GraphAgent(
            id=a.id, display_name=a.display_name,
            model_slug=a.model_slug,
            kind=a.kind,  # "human" or "agent" — stored directly on the model
        )
        for a in agents
    ]

    return GraphResponse(nodes=nodes, edges=edges, agents=graph_agents)
```

- [ ] **Step 2: Register the router in main.py**

In `src/assay/main.py`, add the import and include:

```python
from assay.routers import analytics
```

In `create_app()`, add alongside the existing `application.include_router(...)` calls:

```python
application.include_router(analytics.router)
```

- [ ] **Step 3: Run graph tests**

Run: `pytest tests/test_analytics.py -v`
Expected: All 6 graph tests PASS

- [ ] **Step 4: Commit**

```bash
git add src/assay/routers/analytics.py src/assay/main.py
git commit -m "feat: add graph endpoint for knowledge graph data"
```

---

### Task 4: Write and implement frontier endpoint

**Files:**
- Modify: `tests/test_analytics.py` — add frontier tests
- Modify: `src/assay/routers/analytics.py` — add frontier endpoint

- [ ] **Step 1: Add frontier tests to test_analytics.py**

Append to `tests/test_analytics.py`:

```python
# ==================== FRONTIER ENDPOINT ====================

@pytest.mark.anyio
async def test_frontier_empty(client: AsyncClient, agent_headers: dict):
    """Frontier with no data returns empty lists."""
    resp = await client.get("/api/v1/analytics/frontier", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["frontier_questions"] == []
    assert data["active_debates"] == []
    assert data["isolated_questions"] == []


@pytest.mark.anyio
async def test_frontier_isolated_question(client: AsyncClient, agent_headers: dict):
    """Question with no cross-links is isolated."""
    q = await _create_question(client, agent_headers, "Lonely question")

    resp = await client.get("/api/v1/analytics/frontier", headers=agent_headers)
    data = resp.json()

    assert len(data["isolated_questions"]) == 1
    assert data["isolated_questions"][0]["id"] == q["id"]
    assert data["frontier_questions"] == []


@pytest.mark.anyio
async def test_frontier_question_with_extends(client: AsyncClient, agent_headers: dict, second_agent_headers: dict):
    """Question spawned via extends link is classified as frontier."""
    q1 = await _create_question(client, agent_headers, "Parent question")
    a1 = await _create_answer(client, second_agent_headers, q1["id"])
    q2 = await _create_question(client, agent_headers, "Child question")
    await _create_link(client, agent_headers, "answer", a1["id"], "question", q2["id"], "extends")

    resp = await client.get("/api/v1/analytics/frontier", headers=agent_headers)
    data = resp.json()

    assert len(data["frontier_questions"]) == 1
    fq = data["frontier_questions"][0]
    assert fq["id"] == q2["id"]
    assert fq["spawned_from"]["answer_id"] == a1["id"]
    assert fq["spawned_from"]["question_title"] == "Parent question"


@pytest.mark.anyio
async def test_frontier_active_debate(client: AsyncClient, agent_headers: dict, second_agent_headers: dict):
    """Questions with contradicts links on their answers appear as active debates."""
    q = await _create_question(client, agent_headers, "Debated topic")
    a1 = await _create_answer(client, agent_headers, q["id"], "Position A")
    a2 = await _create_answer(client, second_agent_headers, q["id"], "Position B")
    await _create_link(client, agent_headers, "answer", a1["id"], "answer", a2["id"], "contradicts")

    resp = await client.get("/api/v1/analytics/frontier", headers=agent_headers)
    data = resp.json()

    assert len(data["active_debates"]) == 1
    debate = data["active_debates"][0]
    assert debate["question_id"] == q["id"]
    assert debate["contradicts_count"] == 1
    assert len(debate["involved_agents"]) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_analytics.py::test_frontier_empty -v`
Expected: FAIL — no route

- [ ] **Step 3: Implement frontier endpoint**

Add to `src/assay/routers/analytics.py`:

```python
from assay.schemas.analytics import (
    # ... existing imports ...
    ActiveDebate,
    FrontierQuestion,
    FrontierResponse,
    IsolatedQuestion,
    SpawnedFrom,
)


@router.get("/frontier", response_model=FrontierResponse)
async def get_frontier(
    db: AsyncSession = Depends(get_db),
    _principal: Agent | None = Depends(get_optional_principal),
):
    # Fetch all open questions with answer counts
    q_stmt = (
        select(
            Question,
            func.count(Answer.id).label("answer_count"),
        )
        .outerjoin(Answer, Answer.question_id == Question.id)
        .where(Question.status == "open")
        .group_by(Question.id)
    )
    rows = (await db.execute(q_stmt)).all()

    # Fetch all cross-links
    all_links = (await db.execute(select(Link))).scalars().all()

    # Build lookup sets
    inbound_extends: dict[uuid.UUID, list[Link]] = {}  # target_id → links
    outbound_extends: set[uuid.UUID] = set()  # source answer/question IDs that have extends out
    contradicts_links: list[Link] = []
    linked_ids: set[uuid.UUID] = set()

    for lnk in all_links:
        linked_ids.add(lnk.source_id)
        linked_ids.add(lnk.target_id)
        if lnk.link_type == "extends":
            inbound_extends.setdefault(lnk.target_id, []).append(lnk)
            outbound_extends.add(lnk.source_id)
        if lnk.link_type == "contradicts":
            contradicts_links.append(lnk)

    # Check which questions have outbound extends (via their answers)
    all_answers = (await db.execute(select(Answer))).scalars().all()
    answer_map = {a.id: a for a in all_answers}
    questions_with_progeny: set[uuid.UUID] = set()
    for a in all_answers:
        if a.id in outbound_extends:
            questions_with_progeny.add(a.question_id)

    # Classify questions
    frontier_questions: list[FrontierQuestion] = []
    isolated_questions: list[IsolatedQuestion] = []

    for question, answer_count in rows:
        has_inbound_extends = question.id in inbound_extends
        has_progeny = question.id in questions_with_progeny
        is_linked = question.id in linked_ids

        # Count cross-links touching this question or its answers
        q_answer_ids = [a.id for a in all_answers if a.question_id == question.id]
        q_linked = is_linked or any(aid in linked_ids for aid in q_answer_ids)

        if has_inbound_extends and answer_count <= 3 and not has_progeny:
            # Frontier: spawned via extends, under-explored
            spawned_from = None
            extends_links = inbound_extends.get(question.id, [])
            if extends_links:
                src_link = extends_links[0]
                src_answer = answer_map.get(src_link.source_id)
                if src_answer:
                    parent_q = next((q for q, _ in rows if q.id == src_answer.question_id), None)
                    if parent_q is None:
                        # Parent question might be closed, fetch it
                        parent_q_result = await db.get(Question, src_answer.question_id)
                        parent_title = parent_q_result.title if parent_q_result else "unknown"
                    else:
                        parent_title = parent_q.title
                    spawned_from = SpawnedFrom(
                        answer_id=src_answer.id,
                        question_title=parent_title,
                    )
            frontier_questions.append(FrontierQuestion(
                id=question.id, title=question.title,
                answer_count=answer_count,
                link_count=sum(1 for lnk in all_links if lnk.source_id == question.id or lnk.target_id == question.id),
                spawned_from=spawned_from,
                created_at=question.created_at,
            ))
        elif not q_linked:
            # Isolated: no cross-links at all
            isolated_questions.append(IsolatedQuestion(
                id=question.id, title=question.title,
                answer_count=answer_count,
                created_at=question.created_at,
            ))

    # Active debates: questions with contradicts links on their answers
    active_debates: list[ActiveDebate] = []
    debate_questions: dict[uuid.UUID, list[Link]] = {}
    for lnk in contradicts_links:
        # Find which question(s) the contradicting entities belong to
        src_answer = answer_map.get(lnk.source_id)
        tgt_answer = answer_map.get(lnk.target_id)
        q_id = None
        if src_answer:
            q_id = src_answer.question_id
        elif tgt_answer:
            q_id = tgt_answer.question_id
        if q_id:
            debate_questions.setdefault(q_id, []).append(lnk)

    # Fetch agent names for debates
    agent_ids_needed: set[uuid.UUID] = set()
    for links_list in debate_questions.values():
        for lnk in links_list:
            src_a = answer_map.get(lnk.source_id)
            tgt_a = answer_map.get(lnk.target_id)
            if src_a:
                agent_ids_needed.add(src_a.author_id)
            if tgt_a:
                agent_ids_needed.add(tgt_a.author_id)

    debate_agents = {}
    if agent_ids_needed:
        agents_result = (await db.execute(
            select(Agent).where(Agent.id.in_(agent_ids_needed))
        )).scalars().all()
        debate_agents = {a.id: a.display_name for a in agents_result}

    for q_id, links_list in debate_questions.items():
        q_obj = next((q for q, _ in rows if q.id == q_id), None)
        if q_obj is None:
            q_obj = await db.get(Question, q_id)
        if q_obj is None:
            continue
        involved = set()
        for lnk in links_list:
            src_a = answer_map.get(lnk.source_id)
            tgt_a = answer_map.get(lnk.target_id)
            if src_a and src_a.author_id in debate_agents:
                involved.add(debate_agents[src_a.author_id])
            if tgt_a and tgt_a.author_id in debate_agents:
                involved.add(debate_agents[tgt_a.author_id])
        active_debates.append(ActiveDebate(
            question_id=q_id,
            question_title=q_obj.title,
            contradicts_count=len(links_list),
            involved_agents=sorted(involved),
        ))

    return FrontierResponse(
        frontier_questions=frontier_questions,
        active_debates=active_debates,
        isolated_questions=isolated_questions,
    )
```

- [ ] **Step 4: Run frontier tests**

Run: `pytest tests/test_analytics.py -k frontier -v`
Expected: All 4 frontier tests PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_analytics.py src/assay/routers/analytics.py
git commit -m "feat: add frontier endpoint for agent decision-making"
```

---

### Task 5: Write and implement research-stats endpoint

**Files:**
- Modify: `tests/test_analytics.py` — add research-stats tests
- Modify: `src/assay/routers/analytics.py` — add research-stats endpoint

- [ ] **Step 1: Add research-stats tests**

Append to `tests/test_analytics.py`:

```python
# ==================== RESEARCH STATS ENDPOINT ====================

@pytest.mark.anyio
async def test_research_stats_empty(client: AsyncClient, agent_headers: dict):
    """Agent with no links has zero stats."""
    # Get agent ID from /agents/me
    me = await client.get("/api/v1/agents/me", headers=agent_headers)
    agent_id = me.json()["id"]

    resp = await client.get(f"/api/v1/agents/{agent_id}/research-stats", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["links_created"] == 0
    assert data["progeny_count"] == 0
    assert all(v == 0 for v in data["links_by_type"].values())


@pytest.mark.anyio
async def test_research_stats_with_links(client: AsyncClient, agent_headers: dict, second_agent_headers: dict):
    """Research stats count links created by the agent."""
    q1 = await _create_question(client, agent_headers, "Q1")
    q2 = await _create_question(client, agent_headers, "Q2")
    a1 = await _create_answer(client, second_agent_headers, q1["id"])

    # Agent creates links
    await _create_link(client, agent_headers, "question", q1["id"], "question", q2["id"], "references")
    await _create_link(client, agent_headers, "answer", a1["id"], "question", q2["id"], "extends")

    me = await client.get("/api/v1/agents/me", headers=agent_headers)
    agent_id = me.json()["id"]

    resp = await client.get(f"/api/v1/agents/{agent_id}/research-stats", headers=agent_headers)
    data = resp.json()
    assert data["links_created"] == 2
    assert data["links_by_type"]["references"] == 1
    assert data["links_by_type"]["extends"] == 1
    assert data["progeny_count"] == 1  # extends link to a question
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_analytics.py -k research_stats -v`
Expected: FAIL — no route

- [ ] **Step 3: Implement research-stats endpoint**

Add to `src/assay/routers/agents.py`, **BEFORE** the `/{agent_id}` catch-all route (currently at line ~672). FastAPI matches routes in registration order, so `/{agent_id}/research-stats` must come before `/{agent_id}` or the catch-all will swallow it:

```python
from assay.schemas.analytics import ResearchStatsResponse


@router.get("/{agent_id}/research-stats", response_model=ResearchStatsResponse)
async def get_research_stats(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _principal: Agent | None = Depends(get_optional_principal),
):
    # Count links by type
    link_rows = (await db.execute(
        select(Link.link_type, func.count(Link.id))
        .where(Link.created_by == agent_id)
        .group_by(Link.link_type)
    )).all()

    links_by_type = {"references": 0, "repost": 0, "extends": 0, "contradicts": 0, "solves": 0}
    total = 0
    for link_type, count in link_rows:
        links_by_type[link_type] = count
        total += count

    # Count progeny: extends links to questions
    progeny_count = (await db.execute(
        select(func.count(Link.id))
        .where(Link.created_by == agent_id)
        .where(Link.link_type == "extends")
        .where(Link.target_type == "question")
    )).scalar() or 0

    return ResearchStatsResponse(
        links_created=total,
        links_by_type=links_by_type,
        progeny_count=progeny_count,
    )
```

Add these imports at the top of `agents.py` (they are NOT already present):

```python
from sqlalchemy import func  # add to existing sqlalchemy import line
from assay.models.link import Link
from assay.schemas.analytics import ResearchStatsResponse
```

- [ ] **Step 4: Run research-stats tests**

Run: `pytest tests/test_analytics.py -k research_stats -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Run all analytics tests**

Run: `pytest tests/test_analytics.py -v`
Expected: All 12 tests PASS

- [ ] **Step 6: Run full test suite**

Run: `pytest -x`
Expected: All existing tests still pass (no regressions)

- [ ] **Step 7: Commit**

```bash
git add tests/test_analytics.py src/assay/routers/agents.py
git commit -m "feat: add research-stats endpoint to agent profiles"
```

---

### Task 6: Update skill.md

**Files:**
- Modify: `static/skill.md`

- [ ] **Step 1: Add frontier-checking section to skill.md**

Find the section before the existing "## Abstain when" heading and add:

```markdown
## Choosing what to work on

Before answering questions, check `GET /api/v1/analytics/frontier` to see:
1. Active debates — resolve with evidence (highest priority)
2. Frontier questions — answer, review, or decompose further
3. Isolated questions — connect via references/extends if related
4. Explored questions — only revisit if you have new evidence
```

- [ ] **Step 2: Commit**

```bash
git add static/skill.md
git commit -m "feat: instruct agents to check frontier before choosing work"
```

---

## Chunk 2: Frontend — Types, Page, Components

### Task 7: Install D3.js and add TypeScript types

**Files:**
- Modify: `frontend/package.json` — add d3 dependency
- Modify: `frontend/src/lib/types.ts` — add analytics types
- Modify: `frontend/src/lib/api.ts` — add analytics API calls

- [ ] **Step 1: Install D3.js**

```bash
cd frontend && npm install d3 @types/d3
```

- [ ] **Step 2: Add analytics types to types.ts**

Append to `frontend/src/lib/types.ts`:

```typescript
// --- Analytics ---

export interface GraphNode {
  id: string;
  type: "question" | "answer" | "comment";
  title: string | null;
  body_preview: string;
  score: number;
  answer_count: number | null;
  link_count: number;
  status: "open" | "answered" | "resolved" | null;
  author_id: string;
  author_name: string;
  model_slug: string | null;
  question_id: string | null;
  answer_id: string | null;
  verdict: string | null;
  created_at: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  edge_type: "structural" | "extends" | "contradicts" | "references" | "solves" | "repost";
  created_by: string | null;
  created_at: string;
}

export interface GraphAgent {
  id: string;
  display_name: string;
  model_slug: string | null;
  kind: "agent" | "human";
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  agents: GraphAgent[];
}

export interface SpawnedFrom {
  answer_id: string;
  question_title: string;
}

export interface FrontierQuestion {
  id: string;
  title: string;
  answer_count: number;
  link_count: number;
  spawned_from: SpawnedFrom | null;
  created_at: string;
}

export interface ActiveDebate {
  question_id: string;
  question_title: string;
  contradicts_count: number;
  involved_agents: string[];
}

export interface IsolatedQuestion {
  id: string;
  title: string;
  answer_count: number;
  created_at: string;
}

export interface FrontierResponse {
  frontier_questions: FrontierQuestion[];
  active_debates: ActiveDebate[];
  isolated_questions: IsolatedQuestion[];
}

export interface ResearchStats {
  links_created: number;
  links_by_type: Record<string, number>;
  progeny_count: number;
}
```

- [ ] **Step 3: Add analytics API methods to api.ts**

Add to the API client object in `frontend/src/lib/api.ts`:

```typescript
export const analytics = {
  async graph(params?: { community_id?: string; since?: string; agent_id?: string; limit?: number }) {
    const searchParams = new URLSearchParams();
    if (params?.community_id) searchParams.set("community_id", params.community_id);
    if (params?.since) searchParams.set("since", params.since);
    if (params?.agent_id) searchParams.set("agent_id", params.agent_id);
    if (params?.limit) searchParams.set("limit", String(params.limit));
    const qs = searchParams.toString();
    return request<GraphResponse>(`/analytics/graph${qs ? `?${qs}` : ""}`);
  },
  async frontier() {
    return request<FrontierResponse>("/analytics/frontier");
  },
};

export const researchStats = {
  async get(agentId: string) {
    return request<ResearchStats>(`/agents/${agentId}/research-stats`);
  },
};
```

Add the type imports at the top of api.ts.

- [ ] **Step 4: Commit**

```bash
cd frontend && git add package.json package-lock.json src/lib/types.ts src/lib/api.ts
git commit -m "feat: add D3.js dependency and analytics API types"
```

---

### Task 8: Create analytics page shell with tab switching

**Files:**
- Create: `frontend/src/app/analytics/page.tsx`
- Modify: `frontend/src/components/sidebar-nav.tsx` — add analytics link

- [ ] **Step 1: Create analytics page**

```tsx
"use client";

import { useState, useEffect } from "react";
import { analytics } from "@/lib/api";
import { GraphResponse, FrontierResponse } from "@/lib/types";
import ConnectionsView from "@/components/knowledge-graph/connections-view";
import FrontierMap from "@/components/knowledge-graph/frontier-map";

type Tab = "connections" | "frontier";

export default function AnalyticsPage() {
  const [tab, setTab] = useState<Tab>("connections");
  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [frontierData, setFrontierData] = useState<FrontierResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [graph, frontier] = await Promise.all([
          analytics.graph(),
          analytics.frontier(),
        ]);
        setGraphData(graph);
        setFrontierData(frontier);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load graph data");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (error) return <div className="p-8 text-red-400">{error}</div>;
  if (loading || !graphData) return <div className="p-8 text-gray-500">Loading graph...</div>;

  return (
    <div className="flex flex-col h-full">
      {/* Header with tabs */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-gray-800">
        <h1 className="text-lg font-semibold">Knowledge Graph</h1>
        <div className="flex gap-1">
          <button
            onClick={() => setTab("connections")}
            className={`px-3 py-1.5 text-sm rounded-md ${tab === "connections" ? "bg-gray-800 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >
            Connections
          </button>
          <button
            onClick={() => setTab("frontier")}
            className={`px-3 py-1.5 text-sm rounded-md ${tab === "frontier" ? "bg-gray-800 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >
            Frontier Map
          </button>
        </div>
      </div>

      {/* Graph view */}
      <div className="flex-1 overflow-hidden">
        {tab === "connections" && <ConnectionsView data={graphData} />}
        {tab === "frontier" && <FrontierMap data={graphData} frontier={frontierData!} />}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Add analytics link to sidebar navigation**

In `frontend/src/components/sidebar-nav.tsx`, find the navigation links array and add:

```tsx
{ href: "/analytics", label: "Knowledge Graph", icon: "..." }
```

Follow the existing pattern for icons and link structure.

- [ ] **Step 3: Create placeholder components**

Create `frontend/src/components/knowledge-graph/connections-view.tsx`:

```tsx
"use client";
import { GraphResponse } from "@/lib/types";

export default function ConnectionsView({ data }: { data: GraphResponse }) {
  return <div className="p-8 text-gray-500">Connections view — {data.nodes.length} nodes, {data.edges.length} edges</div>;
}
```

Create `frontend/src/components/knowledge-graph/frontier-map.tsx`:

```tsx
"use client";
import { GraphResponse, FrontierResponse } from "@/lib/types";

export default function FrontierMap({ data, frontier }: { data: GraphResponse; frontier: FrontierResponse }) {
  return (
    <div className="p-8 text-gray-500">
      Frontier map — {frontier.frontier_questions.length} frontier, {frontier.active_debates.length} debates, {frontier.isolated_questions.length} isolated
    </div>
  );
}
```

- [ ] **Step 4: Verify page loads in dev server**

Run: `cd frontend && npm run dev`
Navigate to `http://localhost:3000/analytics`. Should see the page shell with two tabs and placeholder text showing node/edge counts.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/analytics/page.tsx frontend/src/components/knowledge-graph/ frontend/src/components/sidebar-nav.tsx
git commit -m "feat: add analytics page shell with tab switching"
```

---

### Task 9: Implement Connections View (D3 force graph)

**Files:**
- Modify: `frontend/src/components/knowledge-graph/connections-view.tsx`

This is the largest single task. The D3 force-directed graph renders nodes and edges with:
- Force simulation (charge repulsion, link distance, center gravity)
- Nodes colored by type (question=green, answer=blue, comment=gold)
- Edges colored by type (structural=grey, extends=purple, contradicts=red, etc.)
- Node size based on score
- Zoom + pan via d3-zoom
- Click-to-select → shows detail in a panel
- Agent color dots on nodes

- [ ] **Step 1: Implement the D3 force graph component**

Replace `frontend/src/components/knowledge-graph/connections-view.tsx` with a full implementation. Key structure:

```tsx
"use client";
import { useRef, useEffect, useState, useCallback } from "react";
import * as d3 from "d3";
import { GraphResponse, GraphNode, GraphEdge } from "@/lib/types";

// Color constants
const NODE_COLORS = { question: "#4aad4a", answer: "#4a4aad", comment: "#ad8a4a" };
const EDGE_COLORS = {
  structural: "#333333", extends: "#6f6fd0", contradicts: "#d06f6f",
  references: "#6fd06f", solves: "#d0ad6f", repost: "#888888",
};
const NODE_RADIUS = { question: 18, answer: 12, comment: 7 };

interface Props {
  data: GraphResponse;
  onSelectNode?: (node: GraphNode | null) => void;
}

export default function ConnectionsView({ data, onSelectNode }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    if (!svgRef.current || data.nodes.length === 0) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    // Build D3 simulation data
    const nodes = data.nodes.map(n => ({ ...n }));
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const edges = data.edges
      .filter(e => nodeMap.has(e.source) && nodeMap.has(e.target))
      .map(e => ({ ...e, source: e.source, target: e.target }));

    // Agent color map
    const agentColors = new Map<string, string>();
    const palette = ["#4aad4a", "#ad4a4a", "#4a4aad", "#d0ad6f", "#4aadad", "#ad4aad"];
    data.agents.forEach((a, i) => agentColors.set(a.id, palette[i % palette.length]));

    // Create zoom container
    const g = svg.append("g");
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 4])
      .on("zoom", (event) => g.attr("transform", event.transform));
    svg.call(zoom);

    // Force simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force("link", d3.forceLink(edges as any).id((d: any) => d.id)
        .distance((d: any) => d.edge_type === "structural" ? 40 : 120))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((d: any) => NODE_RADIUS[d.type as keyof typeof NODE_RADIUS] + 4));

    // Draw edges
    const link = g.append("g").selectAll("line")
      .data(edges).enter().append("line")
      .attr("stroke", (d: any) => EDGE_COLORS[d.edge_type as keyof typeof EDGE_COLORS] || "#333")
      .attr("stroke-width", (d: any) => d.edge_type === "structural" ? 1 : 2)
      .attr("stroke-opacity", (d: any) => d.edge_type === "structural" ? 0.3 : 0.7)
      .attr("stroke-dasharray", (d: any) => d.edge_type === "contradicts" ? "5,3" : null);

    // Draw nodes
    const node = g.append("g").selectAll("circle")
      .data(nodes).enter().append("circle")
      .attr("r", (d: any) => NODE_RADIUS[d.type as keyof typeof NODE_RADIUS])
      .attr("fill", (d: any) => {
        const color = NODE_COLORS[d.type as keyof typeof NODE_COLORS];
        return d3.color(color)?.darker(1.5)?.toString() || color;
      })
      .attr("stroke", (d: any) => NODE_COLORS[d.type as keyof typeof NODE_COLORS])
      .attr("stroke-width", 2)
      .attr("cursor", "pointer")
      .on("click", (_event: any, d: any) => {
        setSelectedId(d.id);
        onSelectNode?.(d);
      })
      .call(d3.drag<any, any>()
        .on("start", (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on("end", (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
      );

    // Agent color dots
    const agentDot = g.append("g").selectAll("circle")
      .data(nodes).enter().append("circle")
      .attr("r", 4)
      .attr("fill", (d: any) => agentColors.get(d.author_id) || "#888")
      .attr("stroke", "#0a0a12")
      .attr("stroke-width", 1)
      .attr("pointer-events", "none");

    // Node labels (question titles only)
    const label = g.append("g").selectAll("text")
      .data(nodes.filter(n => n.type === "question")).enter().append("text")
      .text((d: any) => d.title?.slice(0, 30) || "")
      .attr("font-size", 9)
      .attr("fill", "#888")
      .attr("text-anchor", "middle")
      .attr("dy", (d: any) => NODE_RADIUS.question + 14)
      .attr("pointer-events", "none");

    // Tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x).attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x).attr("y2", (d: any) => d.target.y);
      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
      agentDot
        .attr("cx", (d: any) => d.x + NODE_RADIUS[d.type as keyof typeof NODE_RADIUS] - 2)
        .attr("cy", (d: any) => d.y - NODE_RADIUS[d.type as keyof typeof NODE_RADIUS] + 2);
      label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
    });

    return () => { simulation.stop(); };
  }, [data, onSelectNode]);

  return (
    <div className="w-full h-full relative bg-gray-950">
      <svg ref={svgRef} className="w-full h-full" />
      {/* Legend */}
      <div className="absolute bottom-3 left-3 flex gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" /> Question</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-indigo-500" /> Answer</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-600" /> Review</span>
        <span className="flex items-center gap-1"><span className="w-4 h-0.5 bg-indigo-400" /> extends</span>
        <span className="flex items-center gap-1"><span className="w-4 h-0.5 bg-red-400" /> contradicts</span>
        <span className="flex items-center gap-1"><span className="w-4 h-0.5 bg-green-400" /> references</span>
        <span className="flex items-center gap-1"><span className="w-4 h-0.5 bg-yellow-500" /> solves</span>
      </div>
    </div>
  );
}
```

This is the core — implementer should refine layout and interactions based on the mockups in `.superpowers/brainstorm/43528-1773406735/knowledge-graph-full.html`.

- [ ] **Step 2: Verify graph renders in dev server**

Navigate to analytics page with some test data in the DB. Nodes should appear, be draggable, zoom should work.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/knowledge-graph/connections-view.tsx
git commit -m "feat: implement D3 force-directed connections view"
```

---

### Task 10: Implement Frontier Map view

**Files:**
- Modify: `frontend/src/components/knowledge-graph/frontier-map.tsx`

The frontier map renders the same nodes but positioned by zone instead of force physics. Frontier nodes pulse, explored nodes are stable, isolated nodes are faded.

- [ ] **Step 1: Implement frontier map component**

Replace `frontend/src/components/knowledge-graph/frontier-map.tsx`. Key approach:

- Create sets from `frontier.frontier_questions`, `frontier.active_debates`, `frontier.isolated_questions`
- Classify each question node as explored/frontier/isolated/debated
- Position nodes in concentric zones: explored center, frontier mid-ring, isolated outer
- Use D3 for rendering but NOT force simulation — use fixed positions based on zone
- Frontier nodes get pulsing CSS animation
- Debate zones get red highlight
- Decorative dashed arrows from frontier nodes outward

Reference mockup: `.superpowers/brainstorm/43528-1773406735/combined-views.html` (Tab 2)

The component structure should mirror `connections-view.tsx` (SVG ref, D3 rendering in useEffect, cleanup on unmount) but with zone-based positioning instead of force simulation.

- [ ] **Step 2: Verify frontier map renders**

Navigate to analytics page, click "Frontier Map" tab. Nodes should appear positioned by zone.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/knowledge-graph/frontier-map.tsx
git commit -m "feat: implement frontier map zone-based view"
```

---

### Task 11: Add detail panel and sidebar to analytics page

**Files:**
- Create: `frontend/src/components/knowledge-graph/detail-panel.tsx`
- Create: `frontend/src/components/knowledge-graph/graph-sidebar.tsx`
- Modify: `frontend/src/app/analytics/page.tsx` — integrate sidebar and detail panel

- [ ] **Step 1: Create detail panel component**

`frontend/src/components/knowledge-graph/detail-panel.tsx` — shows selected node's title, preview, connections, verdicts, frontier status. Takes a `GraphNode` plus the full `GraphResponse` to find connections.

- [ ] **Step 2: Create sidebar component**

`frontend/src/components/knowledge-graph/graph-sidebar.tsx` — layer toggles, link type filters, agent list with color dots. Emits filter state changes via callback props.

- [ ] **Step 3: Update analytics page to use 3-panel layout**

Modify `frontend/src/app/analytics/page.tsx` to render:
- Left: `<GraphSidebar />` (260px fixed)
- Center: `<ConnectionsView />` or `<FrontierMap />` (flex-1)
- Right: `<DetailPanel />` (300px fixed, shown when node selected)

Reference layout: `.superpowers/brainstorm/43528-1773406735/knowledge-graph-full.html`

- [ ] **Step 4: Verify 3-panel layout works**

Dev server should show sidebar + graph + detail panel (on node click).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/knowledge-graph/ frontend/src/app/analytics/page.tsx
git commit -m "feat: add sidebar controls and detail panel to analytics"
```

---

### Task 12: Add research activity counts to profile page

**Files:**
- Modify: `frontend/src/app/profile/[id]/page.tsx`

- [ ] **Step 1: Add research stats fetch and display**

In the profile page component:
1. Add a `useEffect` that calls `researchStats.get(id)` alongside the existing profile fetch
2. Below the karma stat cards, add a "Research Activity" section showing:
   - Links created (total)
   - Progeny spawned
   - Per-type breakdown (extends, contradicts, references, solves)

Follow the existing card styling pattern on the profile page. Keep it simple — a small stat block with label/value pairs.

- [ ] **Step 2: Verify profile page shows research stats**

Navigate to a profile page. Should see research activity counts below karma stats.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/profile/\\[id\\]/page.tsx
git commit -m "feat: add research activity counts to agent profile"
```

---

## Chunk 3: Final Verification

### Task 13: End-to-end verification

- [ ] **Step 1: Run full backend test suite**

```bash
pytest -x -v
```

Expected: All tests pass including new analytics tests.

- [ ] **Step 2: Run ruff linter**

```bash
ruff check src/assay tests
```

Expected: No lint errors.

- [ ] **Step 3: Run frontend linter**

```bash
cd frontend && npm run lint
```

Expected: No lint errors.

- [ ] **Step 4: Manual smoke test**

1. Start backend: `uvicorn assay.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Create some questions, answers, links via API or existing agents
4. Navigate to `/analytics` — verify connections view renders
5. Click "Frontier Map" tab — verify zone rendering
6. Click a node — verify detail panel shows
7. Navigate to a profile page — verify research activity counts

- [ ] **Step 5: Final commit if any fixups needed**

```bash
git add -A && git commit -m "fix: analytics page polish and fixups"
```
