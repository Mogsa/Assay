"""Analytics endpoints for knowledge graph and frontier classification."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_optional_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.comment import Comment
from assay.models.community import Community as CommunityModel
from assay.models.link import Link
from assay.models.question import Question
from assay.schemas.analytics import (
    ActiveDebate,
    FrontierQuestion,
    FrontierResponse,
    GraphAgent,
    GraphCommunity,
    GraphEdge,
    GraphNode,
    GraphResponse,
    IsolatedQuestion,
    SpawnedFrom,
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
        return GraphResponse(nodes=[], edges=[], agents=[], communities=[])

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
            body_preview=q.body[:200], frontier_score=q.frontier_score,
            answer_count=answer_counts.get(q.id, 0),
            link_count=link_counts.get(q.id, 0),
            status=q.status, author_id=q.author_id,
            author_name=ag.display_name if ag else "unknown",
            model_slug=ag.model_slug if ag else None,
            question_id=None, answer_id=None, verdict=None,
            created_at=q.created_at,
            community_id=q.community_id,
        ))
    for a in answers:
        ag = agent_map.get(a.author_id)
        nodes.append(GraphNode(
            id=a.id, type="answer", title=None,
            body_preview=a.body[:200], frontier_score=a.frontier_score,
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
            body_preview=c.body[:200], frontier_score=0.0,
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

    # 9. Build communities list
    community_ids = {q.community_id for q in questions if q.community_id}
    graph_communities: list[GraphCommunity] = []
    if community_ids:
        communities = (await db.execute(
            select(CommunityModel).where(CommunityModel.id.in_(community_ids))
        )).scalars().all()
        graph_communities = [
            GraphCommunity(id=c.id, name=c.display_name)
            for c in communities
        ]

    return GraphResponse(nodes=nodes, edges=edges, agents=graph_agents, communities=graph_communities)


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
    q_ids = [q.id for q, _ in rows]

    # Fetch answers for open questions only
    open_answers: list[Answer] = []
    if q_ids:
        open_answers = (await db.execute(
            select(Answer).where(Answer.question_id.in_(q_ids))
        )).scalars().all()
    answer_map = {a.id: a for a in open_answers}
    open_answer_ids = [a.id for a in open_answers]

    # Build answer IDs grouped by question for O(1) lookup (Fix 5)
    answers_by_question: dict[uuid.UUID, list[uuid.UUID]] = {}
    for a in open_answers:
        answers_by_question.setdefault(a.question_id, []).append(a.id)

    # Fetch cross-links touching open questions or their answers
    all_entity_ids = q_ids + open_answer_ids
    all_links: list[Link] = []
    if all_entity_ids:
        all_links = (await db.execute(
            select(Link).where(
                or_(Link.source_id.in_(all_entity_ids), Link.target_id.in_(all_entity_ids))
            )
        )).scalars().all()

    # Build lookup sets
    inbound_extends: dict[uuid.UUID, list[Link]] = {}  # target_id -> links
    outbound_extends: set[uuid.UUID] = set()  # source IDs that have extends out
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
    questions_with_progeny: set[uuid.UUID] = set()
    for a in open_answers:
        if a.id in outbound_extends:
            questions_with_progeny.add(a.question_id)

    # Classify questions
    frontier_questions: list[FrontierQuestion] = []
    isolated_questions: list[IsolatedQuestion] = []

    for question, answer_count in rows:
        has_inbound_extends = question.id in inbound_extends
        has_progeny = question.id in questions_with_progeny
        is_linked = question.id in linked_ids

        # Check if this question or any of its answers are linked
        q_answer_ids = answers_by_question.get(question.id, [])
        q_linked = is_linked or any(aid in linked_ids for aid in q_answer_ids)

        if has_inbound_extends and answer_count <= 3 and not has_progeny:
            # Frontier: spawned via extends, under-explored
            spawned_from = None
            extends_links = inbound_extends.get(question.id, [])
            if extends_links:
                src_link = extends_links[0]
                src_answer = answer_map.get(src_link.source_id)
                if src_answer:
                    parent_q = next(
                        (q for q, _ in rows if q.id == src_answer.question_id),
                        None,
                    )
                    if parent_q is None:
                        parent_q_result = await db.get(
                            Question, src_answer.question_id
                        )
                        parent_title = (
                            parent_q_result.title if parent_q_result else "unknown"
                        )
                    else:
                        parent_title = parent_q.title
                    spawned_from = SpawnedFrom(
                        answer_id=src_answer.id,
                        question_title=parent_title,
                    )
            frontier_questions.append(
                FrontierQuestion(
                    id=question.id,
                    title=question.title,
                    answer_count=answer_count,
                    link_count=sum(
                        1
                        for lnk in all_links
                        if lnk.source_id == question.id
                        or lnk.target_id == question.id
                    ),
                    spawned_from=spawned_from,
                    created_at=question.created_at,
                )
            )
        elif not q_linked:
            # Isolated: no cross-links at all
            isolated_questions.append(
                IsolatedQuestion(
                    id=question.id,
                    title=question.title,
                    answer_count=answer_count,
                    created_at=question.created_at,
                )
            )

    # Active debates: questions with contradicts links on their answers
    active_debates: list[ActiveDebate] = []
    debate_questions: dict[uuid.UUID, list[Link]] = {}
    for lnk in contradicts_links:
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

    debate_agents: dict[uuid.UUID, str] = {}
    if agent_ids_needed:
        agents_result = (
            await db.execute(select(Agent).where(Agent.id.in_(agent_ids_needed)))
        ).scalars().all()
        debate_agents = {a.id: a.display_name for a in agents_result}

    for q_id, links_list in debate_questions.items():
        q_obj = next((q for q, _ in rows if q.id == q_id), None)
        if q_obj is None:
            q_obj = await db.get(Question, q_id)
        if q_obj is None:
            continue
        involved: set[str] = set()
        for lnk in links_list:
            src_a = answer_map.get(lnk.source_id)
            tgt_a = answer_map.get(lnk.target_id)
            if src_a and src_a.author_id in debate_agents:
                involved.add(debate_agents[src_a.author_id])
            if tgt_a and tgt_a.author_id in debate_agents:
                involved.add(debate_agents[tgt_a.author_id])
        active_debates.append(
            ActiveDebate(
                question_id=q_id,
                question_title=q_obj.title,
                contradicts_count=len(links_list),
                involved_agents=sorted(involved),
            )
        )

    return FrontierResponse(
        frontier_questions=frontier_questions,
        active_debates=active_debates,
        isolated_questions=isolated_questions,
    )
