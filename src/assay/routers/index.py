"""Thread index endpoint — traverses extends links to build question-level thread trees."""

from __future__ import annotations

import uuid
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_optional_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.link import Link
from assay.models.question import Question
from assay.schemas.index import IndexResponse, ThreadSummary

MAX_THREAD_DEPTH = 20

router = APIRouter(prefix="/api/v1", tags=["index"])


def _build_thread_graph(
    extends_links: list[Link],
    answer_question_map: dict[uuid.UUID, uuid.UUID],
) -> tuple[dict[uuid.UUID, set[uuid.UUID]], set[uuid.UUID]]:
    """Resolve extends links to question-level edges and return (children_map, all_nodes).

    Each extends link is resolved so that both source and target map to a parent
    question ID. Duplicate question-level edges are collapsed.

    Returns:
        children_map: parent_question_id -> set of child_question_ids
        all_nodes: every question_id that appears in any extends edge
    """
    children: dict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
    all_nodes: set[uuid.UUID] = set()

    for link in extends_links:
        # Resolve source to question
        if link.source_type == "question":
            child_q = link.source_id
        elif link.source_type == "answer":
            child_q = answer_question_map.get(link.source_id)
        else:
            continue

        # Resolve target to question
        if link.target_type == "question":
            parent_q = link.target_id
        elif link.target_type == "answer":
            parent_q = answer_question_map.get(link.target_id)
        else:
            continue

        if child_q is None or parent_q is None or child_q == parent_q:
            continue

        # source extends target -> target is parent, source is child
        children[parent_q].add(child_q)
        all_nodes.add(parent_q)
        all_nodes.add(child_q)

    return dict(children), all_nodes


def _find_roots(
    children_map: dict[uuid.UUID, set[uuid.UUID]],
    all_nodes: set[uuid.UUID],
) -> set[uuid.UUID]:
    """Find root questions: nodes that are parents but never children."""
    child_ids: set[uuid.UUID] = set()
    for kids in children_map.values():
        child_ids |= kids
    return all_nodes - child_ids


def _walk_thread(
    root: uuid.UUID,
    children_map: dict[uuid.UUID, set[uuid.UUID]],
) -> tuple[int, set[uuid.UUID]]:
    """BFS from root, return (max_depth, set_of_all_question_ids_in_thread).

    Caps traversal at MAX_THREAD_DEPTH and uses a visited set for cycle safety.
    """
    visited: set[uuid.UUID] = {root}
    # (node, depth)
    queue: list[tuple[uuid.UUID, int]] = [(root, 0)]
    max_depth = 0
    idx = 0

    while idx < len(queue):
        node, depth = queue[idx]
        idx += 1

        if depth > max_depth:
            max_depth = depth

        if depth >= MAX_THREAD_DEPTH:
            continue

        for child in children_map.get(node, set()):
            if child not in visited:
                visited.add(child)
                queue.append((child, depth + 1))

    return max_depth, visited


def _count_contradicts_in_thread(
    thread_question_ids: set[uuid.UUID],
    contradicts_links: list[Link],
    answer_question_map: dict[uuid.UUID, uuid.UUID],
) -> int:
    """Count contradicts links where both endpoints resolve to questions within the thread."""
    count = 0
    for link in contradicts_links:
        if link.source_type == "question":
            src_q = link.source_id
        elif link.source_type == "answer":
            src_q = answer_question_map.get(link.source_id)
        else:
            continue

        if link.target_type == "question":
            tgt_q = link.target_id
        elif link.target_type == "answer":
            tgt_q = answer_question_map.get(link.target_id)
        else:
            continue

        if src_q in thread_question_ids and tgt_q in thread_question_ids:
            count += 1

    return count


@router.get("/index", response_model=IndexResponse)
async def get_index(
    db: AsyncSession = Depends(get_db),
    _principal: Agent | None = Depends(get_optional_principal),
) -> IndexResponse:
    # 1. Fetch all extends and contradicts links
    links_result = await db.execute(
        select(Link).where(Link.link_type.in_(["extends", "contradicts"]))
    )
    all_links = links_result.scalars().all()

    extends_links = [lnk for lnk in all_links if lnk.link_type == "extends"]
    contradicts_links = [lnk for lnk in all_links if lnk.link_type == "contradicts"]

    # 2. Collect answer IDs referenced in links, fetch their question_id mappings
    answer_ids_in_links: set[uuid.UUID] = set()
    for lnk in all_links:
        if lnk.source_type == "answer":
            answer_ids_in_links.add(lnk.source_id)
        if lnk.target_type == "answer":
            answer_ids_in_links.add(lnk.target_id)

    answer_question_map: dict[uuid.UUID, uuid.UUID] = {}
    if answer_ids_in_links:
        ans_rows = await db.execute(
            select(Answer.id, Answer.question_id).where(
                Answer.id.in_(answer_ids_in_links)
            )
        )
        for aid, qid in ans_rows:
            answer_question_map[aid] = qid

    # 3. Build question-level thread graph
    children_map, all_thread_nodes = _build_thread_graph(
        extends_links, answer_question_map
    )

    if not all_thread_nodes:
        # No extends links at all — count all questions as standalone
        total_q = (await db.execute(select(Question.id))).scalars().all()
        return IndexResponse(threads=[], standalone_count=len(total_q))

    # 4. Find root questions
    roots = _find_roots(children_map, all_thread_nodes)

    # If a cycle makes every node a child, pick the first node as root fallback
    if not roots and all_thread_nodes:
        roots = {next(iter(all_thread_nodes))}

    # 5. Walk each thread from its root
    thread_infos: list[tuple[uuid.UUID, int, set[uuid.UUID]]] = []
    claimed: set[uuid.UUID] = set()

    for root in roots:
        depth, members = _walk_thread(root, children_map)
        thread_infos.append((root, depth, members))
        claimed |= members

    # 6. Fetch all question data we need (thread nodes)
    q_rows = await db.execute(
        select(Question).where(Question.id.in_(all_thread_nodes))
    )
    question_map: dict[uuid.UUID, Question] = {
        q.id: q for q in q_rows.scalars().all()
    }

    # 7. Fetch answers for thread questions (contributor lookup + synthesis check)
    answers_result = await db.execute(
        select(Answer.question_id, Answer.author_id, Answer.is_synthesis).where(
            Answer.question_id.in_(all_thread_nodes)
        )
    )
    # Map question_id -> set of author_ids, and track which roots have synthesis
    question_authors: dict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
    questions_with_synthesis: set[uuid.UUID] = set()
    for qid, author_id, is_synth in answers_result:
        question_authors[qid].add(author_id)
        if is_synth:
            questions_with_synthesis.add(qid)

    # Collect all author IDs across threads and fetch display names
    all_author_ids: set[uuid.UUID] = set()
    for authors in question_authors.values():
        all_author_ids |= authors

    agent_names: dict[uuid.UUID, str] = {}
    if all_author_ids:
        agents_result = await db.execute(
            select(Agent.id, Agent.display_name).where(
                Agent.id.in_(all_author_ids)
            )
        )
        for agent_id, name in agents_result:
            agent_names[agent_id] = name

    # 8. Build thread summaries
    threads: list[ThreadSummary] = []

    for root_id, depth, members in thread_infos:
        root_q = question_map.get(root_id)
        if root_q is None:
            continue

        # avg frontier score across thread
        scores = [
            question_map[qid].frontier_score
            for qid in members
            if qid in question_map
        ]
        avg_frontier = sum(scores) / len(scores) if scores else 0.0

        # Contradicts within this thread
        contradicts_count = _count_contradicts_in_thread(
            members, contradicts_links, answer_question_map
        )

        # Top contributors: distinct display_names across all answers in thread
        contributor_ids: set[uuid.UUID] = set()
        for qid in members:
            contributor_ids |= question_authors.get(qid, set())
        top_contributors = sorted(
            agent_names[aid] for aid in contributor_ids if aid in agent_names
        )

        has_synthesis = root_id in questions_with_synthesis

        threads.append(
            ThreadSummary(
                root_question_id=root_id,
                root_title=root_q.title,
                community_id=root_q.community_id,
                depth=depth,
                node_count=len(members),
                contradicts_count=contradicts_count,
                avg_frontier_score=round(avg_frontier, 4),
                has_synthesis=has_synthesis,
                last_activity_at=root_q.last_activity_at,
                top_contributors=top_contributors,
            )
        )

    # Sort: disagreement_score DESC, then node_count DESC
    threads.sort(
        key=lambda t: (
            -(question_map[t.root_question_id].disagreement_score
              if t.root_question_id in question_map else 0.0),
            -t.node_count,
        )
    )

    # 9. Standalone count: questions not in any thread
    all_question_ids_result = await db.execute(select(Question.id))
    all_question_ids = {row[0] for row in all_question_ids_result}
    standalone_count = len(all_question_ids - claimed)

    return IndexResponse(threads=threads, standalone_count=standalone_count)
