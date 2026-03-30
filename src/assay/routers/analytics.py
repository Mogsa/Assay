"""Analytics endpoints for knowledge graph and frontier classification."""

from __future__ import annotations

import hashlib
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone

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
from assay.models.rating import Rating
from assay.schemas.analytics import (
    ActiveDebate,
    ArcContributor,
    ArcSummary,
    ArcsResponse,
    FrontierQuestion,
    FrontierResponse,
    GraphAgent,
    GraphCommunity,
    GraphEdge,
    GraphNode,
    GraphResponse,
    IsolatedQuestion,
)

EXPLORED_THRESHOLD = 4    # answer_count >= this → "explored"
FRONTIER_MAX_ANSWERS = 3  # answer_count <= this → eligible for frontier

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/graph", response_model=GraphResponse)
async def get_graph(
    db: AsyncSession = Depends(get_db),
    _principal: Agent | None = Depends(get_optional_principal),
    community_id: uuid.UUID | None = None,
    since: datetime | None = None,
    agent_id: uuid.UUID | None = None,
    question_ids: str | None = Query(default=None, description="Comma-separated question UUIDs to filter to"),
    limit: int = Query(default=200, le=500),
):
    # 1. Fetch questions
    if question_ids:
        qid_list = []
        for qid in question_ids.split(","):
            qid = qid.strip()
            if not qid:
                continue
            try:
                qid_list.append(uuid.UUID(qid))
            except ValueError:
                continue
        qid_list = qid_list[:500]  # cap to prevent unbounded IN clause
        q_stmt = select(Question).where(Question.id.in_(qid_list)) if qid_list else select(Question).limit(0)
    else:
        q_stmt = select(Question).order_by(Question.created_at.desc()).limit(limit)
    if not question_ids and community_id:
        q_stmt = q_stmt.where(Question.community_id == community_id)
    if not question_ids and since:
        q_stmt = q_stmt.where(Question.created_at >= since)
    if not question_ids and agent_id:
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

    # Build question_of: maps both question IDs and answer IDs to parent question ID
    question_of: dict[uuid.UUID, uuid.UUID] = {}
    for q, _ in rows:
        question_of[q.id] = q.id
    for a in open_answers:
        question_of[a.id] = a.question_id

    # Build linked_neighbors: lift all links to question-level adjacency
    linked_neighbors: dict[uuid.UUID, set[uuid.UUID]] = {}
    contradicts_links: list[Link] = []
    linked_ids: set[uuid.UUID] = set()

    for lnk in all_links:
        linked_ids.add(lnk.source_id)
        linked_ids.add(lnk.target_id)
        src_q = question_of.get(lnk.source_id)
        tgt_q = question_of.get(lnk.target_id)
        if src_q and tgt_q and src_q != tgt_q:
            linked_neighbors.setdefault(src_q, set()).add(tgt_q)
            linked_neighbors.setdefault(tgt_q, set()).add(src_q)
        if lnk.link_type == "contradicts":
            contradicts_links.append(lnk)

    # Compute explored_ids: questions with enough answers
    answer_counts: dict[uuid.UUID, int] = {q.id: cnt for q, cnt in rows}
    explored_ids: set[uuid.UUID] = {
        qid for qid, cnt in answer_counts.items() if cnt >= EXPLORED_THRESHOLD
    }

    # Classify questions
    frontier_questions: list[FrontierQuestion] = []
    isolated_questions: list[IsolatedQuestion] = []

    for question, answer_count in rows:
        neighbors = linked_neighbors.get(question.id, set())
        touches_explored = bool(neighbors & explored_ids)

        # Check if this question or any of its answers are linked
        q_answer_ids = answers_by_question.get(question.id, [])
        q_linked = question.id in linked_ids or any(
            aid in linked_ids for aid in q_answer_ids
        )

        if (
            touches_explored
            and answer_count <= FRONTIER_MAX_ANSWERS
            and question.status != "resolved"
        ):
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
                    created_at=question.created_at,
                )
            )
        elif not q_linked:
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


# ---- Contributor scoring constants ----
SCORE_RATING = 1
SCORE_ANSWER = 2
SCORE_REVIEW = 2  # comment on answer
SCORE_QUESTION = 3
SCORE_CONTRADICTS_LINK = 5
BONUS_PROLIFIC_QUESTION = 5  # question spawns 3+ answers

RECENCY_WINDOW = timedelta(hours=24)


def _compute_lifecycle(
    contradicts_count: int,
    last_activity: datetime,
    now: datetime,
) -> str:
    """Classify arc lifecycle based on contradicts and recency."""
    recent = (now - last_activity) < RECENCY_WINDOW
    if contradicts_count > 0 and recent:
        return "contested"
    if recent:
        return "growing"
    if contradicts_count > 0:
        return "converging"
    return "resolved"


def _longest_path_from(
    node: uuid.UUID,
    children: dict[uuid.UUID, list[uuid.UUID]],
) -> int:
    """DFS to find longest directed path length from node."""
    best = 0
    for child in children.get(node, []):
        best = max(best, 1 + _longest_path_from(child, children))
    return best


@router.get("/arcs", response_model=ArcsResponse)
async def get_arcs(
    db: AsyncSession = Depends(get_db),
    _principal: Agent | None = Depends(get_optional_principal),
    limit: int = Query(default=50, le=200),
) -> ArcsResponse:
    """Return question arcs — connected components via extends/contradicts links."""

    # 1. Load all question-to-question extends + contradicts links
    link_stmt = select(Link).where(
        and_(
            Link.source_type == "question",
            Link.target_type == "question",
            Link.link_type.in_(["extends", "contradicts"]),
        )
    )
    all_edges = (await db.execute(link_stmt)).scalars().all()

    if not all_edges:
        return ArcsResponse(arcs=[], total=0)

    # 2. Build adjacency structures
    # Undirected for component detection
    undirected: dict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
    # Directed: parent -> children (extends only, for depth calc)
    # extends: source extends target => target is parent, source is child
    children: dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    # Incoming extends count (to find roots — nodes with 0 incoming)
    incoming_extends: dict[uuid.UUID, int] = defaultdict(int)

    extends_count_total: dict[uuid.UUID, int] = defaultdict(int)  # per-node
    contradicts_count_total: dict[uuid.UUID, int] = defaultdict(int)

    all_question_ids: set[uuid.UUID] = set()

    for edge in all_edges:
        undirected[edge.source_id].add(edge.target_id)
        undirected[edge.target_id].add(edge.source_id)
        all_question_ids.add(edge.source_id)
        all_question_ids.add(edge.target_id)

        if edge.link_type == "extends":
            # source extends target => target is parent of source
            children[edge.target_id].append(edge.source_id)
            incoming_extends[edge.source_id] += 1
            extends_count_total[edge.source_id] += 1
            extends_count_total[edge.target_id] += 0  # ensure key exists
        elif edge.link_type == "contradicts":
            contradicts_count_total[edge.source_id] += 1
            contradicts_count_total[edge.target_id] += 0

    # 3. BFS to find connected components
    visited: set[uuid.UUID] = set()
    components: list[set[uuid.UUID]] = []

    for node in all_question_ids:
        if node in visited:
            continue
        component: set[uuid.UUID] = set()
        queue = [node]
        while queue:
            current = queue.pop()
            if current in visited:
                continue
            visited.add(current)
            component.add(current)
            for neighbor in undirected[current]:
                if neighbor not in visited:
                    queue.append(neighbor)
        components.append(component)

    # 4. Fetch all questions in these components
    q_stmt = select(Question).where(Question.id.in_(all_question_ids))
    questions = (await db.execute(q_stmt)).scalars().all()
    q_map: dict[uuid.UUID, Question] = {q.id: q for q in questions}

    # 5. Fetch answers, comments, ratings for engagement + contributor scoring
    answer_stmt = select(Answer).where(Answer.question_id.in_(all_question_ids))
    answers = (await db.execute(answer_stmt)).scalars().all()
    answers_by_q: dict[uuid.UUID, list[Answer]] = defaultdict(list)
    for a in answers:
        answers_by_q[a.question_id].append(a)

    answer_ids = [a.id for a in answers]

    comments: list[Comment] = []
    if answer_ids:
        comment_stmt = select(Comment).where(
            and_(Comment.target_type == "answer", Comment.target_id.in_(answer_ids))
        )
        comments = (await db.execute(comment_stmt)).scalars().all()

    # Ratings on questions and answers in these arcs
    ratable_ids = list(all_question_ids) + answer_ids
    ratings: list[Rating] = []
    if ratable_ids:
        rating_stmt = select(Rating).where(Rating.target_id.in_(ratable_ids))
        ratings = (await db.execute(rating_stmt)).scalars().all()

    # Index comments and ratings by question
    comments_by_q: dict[uuid.UUID, list[Comment]] = defaultdict(list)
    answer_id_to_q: dict[uuid.UUID, uuid.UUID] = {
        a.id: a.question_id for a in answers
    }
    for c in comments:
        q_id = answer_id_to_q.get(c.target_id)
        if q_id:
            comments_by_q[q_id].append(c)

    ratings_by_q: dict[uuid.UUID, list[Rating]] = defaultdict(list)
    for r in ratings:
        # Direct question rating
        if r.target_id in all_question_ids:
            ratings_by_q[r.target_id].append(r)
        # Answer rating -> map to question
        q_id = answer_id_to_q.get(r.target_id)
        if q_id:
            ratings_by_q[q_id].append(r)

    # 6. Fetch agents for contributor info
    agent_ids: set[uuid.UUID] = set()
    for q in questions:
        agent_ids.add(q.author_id)
    for a in answers:
        agent_ids.add(a.author_id)
    for c in comments:
        agent_ids.add(c.author_id)
    for r in ratings:
        agent_ids.add(r.rater_id)
    for edge in all_edges:
        agent_ids.add(edge.created_by)

    agents = (
        await db.execute(select(Agent).where(Agent.id.in_(agent_ids)))
    ).scalars().all()
    agent_map: dict[uuid.UUID, Agent] = {a.id: a for a in agents}

    # 7. Fetch community names
    community_ids = {q.community_id for q in questions if q.community_id}
    community_map: dict[uuid.UUID, str] = {}
    if community_ids:
        communities = (
            await db.execute(
                select(CommunityModel).where(CommunityModel.id.in_(community_ids))
            )
        ).scalars().all()
        community_map = {c.id: c.display_name for c in communities}

    # 8. Build arc summaries
    now = datetime.now(timezone.utc)
    arc_summaries: list[ArcSummary] = []

    for component in components:
        # Find root: question with no incoming extends; ties broken by earliest created_at
        root_candidates = [
            qid for qid in component if incoming_extends.get(qid, 0) == 0
        ]
        if not root_candidates:
            # Cycle — pick earliest
            root_candidates = list(component)

        root_candidates.sort(
            key=lambda qid: q_map[qid].created_at if qid in q_map else now
        )
        root_id = root_candidates[0]
        root_q = q_map.get(root_id)
        if root_q is None:
            continue

        # Depth: longest directed path from root
        depth = _longest_path_from(root_id, children)

        # Count links in this component
        comp_extends = sum(
            1
            for e in all_edges
            if e.link_type == "extends"
            and e.source_id in component
            and e.target_id in component
        )
        comp_contradicts = sum(
            1
            for e in all_edges
            if e.link_type == "contradicts"
            and e.source_id in component
            and e.target_id in component
        )

        # Engagement inputs
        comp_answers = sum(len(answers_by_q.get(qid, [])) for qid in component)
        comp_comments = sum(len(comments_by_q.get(qid, [])) for qid in component)
        comp_ratings = sum(len(ratings_by_q.get(qid, [])) for qid in component)

        engagement = (comp_answers + comp_comments + comp_ratings) * (
            1 + comp_contradicts * 5
        )

        # Contributor scoring
        scores: dict[uuid.UUID, int] = defaultdict(int)
        for qid in component:
            q = q_map.get(qid)
            if q:
                scores[q.author_id] += SCORE_QUESTION
                # Bonus: question with 3+ answers
                if len(answers_by_q.get(qid, [])) >= 3:
                    scores[q.author_id] += BONUS_PROLIFIC_QUESTION

            for a in answers_by_q.get(qid, []):
                scores[a.author_id] += SCORE_ANSWER
            for c in comments_by_q.get(qid, []):
                scores[c.author_id] += SCORE_REVIEW
            for r in ratings_by_q.get(qid, []):
                scores[r.rater_id] += SCORE_RATING

        # Contradicts link creators get bonus
        for edge in all_edges:
            if (
                edge.link_type == "contradicts"
                and edge.source_id in component
                and edge.target_id in component
            ):
                scores[edge.created_by] += SCORE_CONTRADICTS_LINK

        contributors = sorted(
            [
                ArcContributor(
                    agent_id=aid,
                    display_name=agent_map[aid].display_name
                    if aid in agent_map
                    else "unknown",
                    model_slug=agent_map[aid].model_slug
                    if aid in agent_map
                    else None,
                    score=s,
                )
                for aid, s in scores.items()
            ],
            key=lambda c: c.score,
            reverse=True,
        )

        # Timestamps
        created_at = min(
            (q_map[qid].created_at for qid in component if qid in q_map),
            default=now,
        )
        last_activity = max(
            (
                q_map[qid].last_activity_at
                for qid in component
                if qid in q_map and q_map[qid].last_activity_at
            ),
            default=created_at,
        )

        lifecycle = _compute_lifecycle(comp_contradicts, last_activity, now)

        # Deterministic arc_id from sorted question UUIDs
        sorted_ids = sorted(str(qid) for qid in component)
        arc_id = hashlib.sha256("".join(sorted_ids).encode()).hexdigest()[:12]

        arc_summaries.append(
            ArcSummary(
                arc_id=arc_id,
                root_question_id=root_id,
                root_question_title=root_q.title,
                question_ids=list(component),
                depth=depth,
                breadth=len(component),
                contradicts_count=comp_contradicts,
                extends_count=comp_extends,
                answer_count=comp_answers,
                rating_count=comp_ratings,
                engagement_score=float(engagement),
                contributors=contributors,
                lifecycle=lifecycle,
                root_community=community_map.get(root_q.community_id)
                if root_q.community_id
                else None,
                created_at=created_at,
                last_activity=last_activity,
            )
        )

    # Sort by engagement descending
    arc_summaries.sort(key=lambda a: a.engagement_score, reverse=True)
    total = len(arc_summaries)
    arc_summaries = arc_summaries[:limit]

    return ArcsResponse(arcs=arc_summaries, total=total)
