"""Analytics endpoints for knowledge graph and frontier classification."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_, and_
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

    # Answer lookup (for comment -> question_id tracing)
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
            kind=a.kind,
        )
        for a in agents
    ]

    return GraphResponse(nodes=nodes, edges=edges, agents=graph_agents)
