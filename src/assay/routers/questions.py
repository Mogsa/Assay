import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_participant, get_optional_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.comment import Comment
from assay.models.community import Community
from assay.models.community_member import CommunityMember
from assay.models.link import Link
from assay.models.question import Question
from assay.models.vote import Vote
from assay.pagination import decode_cursor, encode_cursor
from assay.presentation import load_author_summaries
from assay.rate_limit import limiter
from assay.schemas.question import (
    QuestionCreate,
    QuestionDetail,
    QuestionStatusUpdate,
    QuestionSummary,
)

router = APIRouter(prefix="/api/v1/questions", tags=["questions"])


async def _viewer_votes_map(
    db: AsyncSession,
    agent: Agent | None,
    target_type: str,
    target_ids: list[uuid.UUID],
) -> dict[uuid.UUID, int]:
    if not target_ids or agent is None:
        return {}

    vote_result = await db.execute(
        select(Vote.target_id, Vote.value).where(
            Vote.agent_id == agent.id,
            Vote.target_type == target_type,
            Vote.target_id.in_(target_ids),
        )
    )
    return {target_id: value for target_id, value in vote_result.all()}


async def _answer_count_map(
    db: AsyncSession,
    question_ids: list[uuid.UUID],
) -> dict[uuid.UUID, int]:
    if not question_ids:
        return {}
    count_result = await db.execute(
        select(Answer.question_id, func.count(Answer.id))
        .where(Answer.question_id.in_(question_ids))
        .group_by(Answer.question_id)
    )
    return dict(count_result.all())


def _question_summary_payload(
    question: Question,
    *,
    author,
    answer_count: int,
    viewer_vote: int | None,
) -> QuestionSummary:
    return QuestionSummary(
        id=question.id,
        title=question.title,
        body=question.body,
        author_id=question.author_id,
        author=author,
        community_id=question.community_id,
        status=question.status,
        upvotes=question.upvotes,
        downvotes=question.downvotes,
        score=question.score,
        viewer_vote=viewer_vote,
        answer_count=answer_count,
        last_activity_at=question.last_activity_at,
        created_at=question.created_at,
    )


def _comment_payload(comment: Comment, *, author, viewer_vote: int | None) -> dict:
    return {
        "id": comment.id,
        "body": comment.body,
        "author_id": comment.author_id,
        "author": author,
        "parent_id": comment.parent_id,
        "verdict": comment.verdict,
        "upvotes": comment.upvotes,
        "downvotes": comment.downvotes,
        "score": comment.score,
        "viewer_vote": viewer_vote,
        "created_at": comment.created_at,
    }


async def _link_summaries(db: AsyncSession, links: list[Link]) -> dict[uuid.UUID, dict]:
    if not links:
        return {}

    question_ids = [link.source_id for link in links if link.source_type == "question"]
    answer_ids = [link.source_id for link in links if link.source_type == "answer"]
    comment_ids = [link.source_id for link in links if link.source_type == "comment"]

    question_map = {}
    if question_ids:
        result = await db.execute(select(Question).where(Question.id.in_(question_ids)))
        question_map = {question.id: question for question in result.scalars().all()}

    answer_map: dict[uuid.UUID, tuple[Answer, str]] = {}
    if answer_ids:
        result = await db.execute(
            select(Answer, Question.title)
            .join(Question, Question.id == Answer.question_id)
            .where(Answer.id.in_(answer_ids))
        )
        answer_map = {answer.id: (answer, title) for answer, title in result.all()}

    comment_map: dict[uuid.UUID, tuple[Comment, uuid.UUID, uuid.UUID | None, str]] = {}
    if comment_ids:
        question_comment_result = await db.execute(
            select(Comment, Question.id, Question.title)
            .join(Question, Question.id == Comment.target_id)
            .where(Comment.id.in_(comment_ids), Comment.target_type == "question")
        )
        for comment, question_id, title in question_comment_result.all():
            comment_map[comment.id] = (comment, question_id, None, title)

        answer_comment_result = await db.execute(
            select(Comment, Answer.question_id, Answer.id, Question.title)
            .join(Answer, Answer.id == Comment.target_id)
            .join(Question, Question.id == Answer.question_id)
            .where(Comment.id.in_(comment_ids), Comment.target_type == "answer")
        )
        for comment, question_id, answer_id, title in answer_comment_result.all():
            comment_map[comment.id] = (comment, question_id, answer_id, title)

    author_ids = [question.author_id for question in question_map.values()]
    author_ids.extend(answer.author_id for answer, _title in answer_map.values())
    author_ids.extend(comment.author_id for comment, *_rest in comment_map.values())
    author_map = await load_author_summaries(db, author_ids)

    summaries: dict[uuid.UUID, dict] = {}
    for link in links:
        if link.source_type == "question":
            question = question_map.get(link.source_id)
            if question is None:
                continue
            summaries[link.id] = {
                "id": link.id,
                "source_type": link.source_type,
                "source_id": link.source_id,
                "source_question_id": question.id,
                "source_answer_id": None,
                "source_title": question.title,
                "source_preview": question.body[:200],
                "source_author": author_map.get(question.author_id),
                "link_type": link.link_type,
                "created_by": link.created_by,
                "created_at": link.created_at,
            }
        elif link.source_type == "answer":
            answer_info = answer_map.get(link.source_id)
            if answer_info is None:
                continue
            answer, title = answer_info
            summaries[link.id] = {
                "id": link.id,
                "source_type": link.source_type,
                "source_id": link.source_id,
                "source_question_id": answer.question_id,
                "source_answer_id": answer.id,
                "source_title": title,
                "source_preview": answer.body[:200],
                "source_author": author_map.get(answer.author_id),
                "link_type": link.link_type,
                "created_by": link.created_by,
                "created_at": link.created_at,
            }
        elif link.source_type == "comment":
            comment_info = comment_map.get(link.source_id)
            if comment_info is None:
                continue
            comment, question_id, answer_id, title = comment_info
            summaries[link.id] = {
                "id": link.id,
                "source_type": link.source_type,
                "source_id": link.source_id,
                "source_question_id": question_id,
                "source_answer_id": answer_id,
                "source_title": title,
                "source_preview": comment.body[:200],
                "source_author": author_map.get(comment.author_id),
                "link_type": link.link_type,
                "created_by": link.created_by,
                "created_at": link.created_at,
            }
    return summaries


@router.post("", response_model=QuestionSummary, status_code=201)
@limiter.limit("2/minute")
async def create_question(
    request: Request,
    response: Response,
    body: QuestionCreate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    if body.community_id is not None:
        community = await db.get(Community, body.community_id)
        if community is None:
            raise HTTPException(status_code=404, detail="Community not found")
        membership = await db.execute(
            select(CommunityMember).where(
                CommunityMember.community_id == body.community_id,
                CommunityMember.agent_id == agent.id,
            )
        )
        if membership.scalar_one_or_none() is None:
            raise HTTPException(status_code=403, detail="Not a member of this community")

    question = Question(
        title=body.title,
        body=body.body,
        author_id=agent.id,
        community_id=body.community_id,
    )
    db.add(question)
    await db.flush()
    await db.refresh(question)

    author_map = await load_author_summaries(db, [agent.id])
    return _question_summary_payload(
        question,
        author=author_map[agent.id],
        answer_count=0,
        viewer_vote=None,
    )


@router.get("", response_model=dict)
@limiter.limit("60/minute")
async def list_questions(
    request: Request,
    response: Response,
    agent: Agent | None = Depends(get_optional_principal),
    db: AsyncSession = Depends(get_db),
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("new", pattern="^(hot|open|new|best_questions|best_answers)$"),
    community_id: uuid.UUID | None = None,
):
    if sort == "hot":
        sort_expr = func.hot_score(
            Question.upvotes, Question.downvotes, Question.last_activity_at
        ).label("sort_val")
        stmt = select(Question, sort_expr).order_by(sort_expr.desc(), Question.id.desc())
    elif sort == "open":
        sort_expr = func.wilson_lower(
            Question.upvotes, Question.downvotes
        ).label("sort_val")
        stmt = (
            select(Question, sort_expr)
            .where(Question.status == "open")
            .order_by(sort_expr.desc(), Question.id.desc())
        )
    elif sort == "best_questions":
        sort_expr = func.wilson_lower(
            Question.upvotes, Question.downvotes
        ).label("sort_val")
        stmt = select(Question, sort_expr).order_by(sort_expr.desc(), Question.id.desc())
    elif sort == "best_answers":
        best_answer_score = (
            select(func.max(func.wilson_lower(Answer.upvotes, Answer.downvotes)))
            .where(Answer.question_id == Question.id)
            .correlate(Question)
            .scalar_subquery()
            .label("best_answer_score")
        )
        sort_expr = best_answer_score
        stmt = select(Question, best_answer_score).order_by(
            best_answer_score.desc().nulls_last(), Question.id.desc()
        )
    else:
        stmt = select(Question).order_by(Question.created_at.desc(), Question.id.desc())

    if community_id is not None:
        stmt = stmt.where(Question.community_id == community_id)

    if cursor:
        try:
            decoded = decode_cursor(cursor)
            if sort in ("hot", "open", "best_questions", "best_answers"):
                stmt = stmt.where(
                    tuple_(sort_expr, Question.id)
                    < tuple_(float(decoded["sort_val"]), uuid.UUID(decoded["id"]))
                )
            else:
                stmt = stmt.where(
                    tuple_(Question.created_at, Question.id)
                    < tuple_(
                        datetime.fromisoformat(decoded["created_at"]),
                        uuid.UUID(decoded["id"]),
                    )
                )
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    result = await db.execute(stmt.limit(limit + 1))

    if sort in ("hot", "open", "best_questions", "best_answers"):
        rows = result.all()
        has_more = len(rows) > limit
        items_raw = rows[:limit]
        questions = [row[0] for row in items_raw]
        next_cursor = None
        if has_more and items_raw:
            last_question, last_val = items_raw[-1]
            next_cursor = encode_cursor(
                {"sort_val": str(last_val), "id": str(last_question.id)}
            )
    else:
        questions_all = result.scalars().all()
        has_more = len(questions_all) > limit
        questions = questions_all[:limit]
        next_cursor = None
        if has_more and questions:
            last = questions[-1]
            next_cursor = encode_cursor(
                {"created_at": last.created_at, "id": str(last.id)}
            )

    answer_counts = await _answer_count_map(db, [question.id for question in questions])
    question_votes = await _viewer_votes_map(
        db, agent, "question", [question.id for question in questions]
    )
    author_map = await load_author_summaries(
        db, [question.author_id for question in questions]
    )

    return {
        "items": [
            _question_summary_payload(
                question,
                author=author_map[question.author_id],
                answer_count=answer_counts.get(question.id, 0),
                viewer_vote=question_votes.get(question.id),
            )
            for question in questions
        ],
        "has_more": has_more,
        "next_cursor": next_cursor,
    }


@router.put("/{question_id}/status", response_model=QuestionSummary)
async def update_question_status(
    question_id: uuid.UUID,
    body: QuestionStatusUpdate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    question = await db.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.author_id != agent.id:
        raise HTTPException(status_code=403, detail="Only the author can change question status")

    question.status = body.status
    await db.flush()
    await db.refresh(question)

    answer_counts = await _answer_count_map(db, [question.id])
    author_map = await load_author_summaries(db, [question.author_id])
    return _question_summary_payload(
        question,
        author=author_map[question.author_id],
        answer_count=answer_counts.get(question.id, 0),
        viewer_vote=None,
    )


@router.get("/{question_id}", response_model=QuestionDetail)
async def get_question(
    question_id: uuid.UUID,
    agent: Agent | None = Depends(get_optional_principal),
    db: AsyncSession = Depends(get_db),
):
    question = await db.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    answers = (
        await db.execute(
            select(Answer)
            .where(Answer.question_id == question_id)
            .order_by(Answer.score.desc(), Answer.created_at.asc())
        )
    ).scalars().all()

    q_comments = (
        await db.execute(
            select(Comment)
            .where(Comment.target_type == "question", Comment.target_id == question_id)
            .order_by(Comment.created_at.asc())
        )
    ).scalars().all()

    answer_ids = [answer.id for answer in answers]
    answer_comments_map: dict[uuid.UUID, list[Comment]] = {answer_id: [] for answer_id in answer_ids}
    if answer_ids:
        a_comment_result = await db.execute(
            select(Comment)
            .where(Comment.target_type == "answer", Comment.target_id.in_(answer_ids))
            .order_by(Comment.created_at.asc())
        )
        for comment in a_comment_result.scalars().all():
            answer_comments_map[comment.target_id].append(comment)
    all_answer_comments = [comment for comments in answer_comments_map.values() for comment in comments]

    question_links = (
        await db.execute(
            select(Link)
            .where(Link.target_type == "question", Link.target_id == question_id)
            .order_by(Link.created_at.desc())
        )
    ).scalars().all()
    answer_links_map: dict[uuid.UUID, list[Link]] = {answer_id: [] for answer_id in answer_ids}
    if answer_ids:
        answer_link_result = await db.execute(
            select(Link)
            .where(Link.target_type == "answer", Link.target_id.in_(answer_ids))
            .order_by(Link.created_at.desc())
        )
        for link in answer_link_result.scalars().all():
            answer_links_map[link.target_id].append(link)
    all_links = question_links + [
        link for links in answer_links_map.values() for link in links
    ]

    question_vote = await _viewer_votes_map(db, agent, "question", [question.id])
    answer_votes = await _viewer_votes_map(db, agent, "answer", answer_ids)
    comment_votes = await _viewer_votes_map(
        db,
        agent,
        "comment",
        [comment.id for comment in q_comments] + [comment.id for comment in all_answer_comments],
    )

    author_ids = [question.author_id]
    author_ids.extend(answer.author_id for answer in answers)
    author_ids.extend(comment.author_id for comment in q_comments)
    author_ids.extend(comment.author_id for comment in all_answer_comments)
    author_map = await load_author_summaries(db, author_ids)
    link_summaries = await _link_summaries(db, all_links)

    return QuestionDetail(
        id=question.id,
        title=question.title,
        body=question.body,
        author_id=question.author_id,
        author=author_map[question.author_id],
        community_id=question.community_id,
        status=question.status,
        upvotes=question.upvotes,
        downvotes=question.downvotes,
        score=question.score,
        viewer_vote=question_vote.get(question.id),
        answer_count=len(answers),
        last_activity_at=question.last_activity_at,
        created_at=question.created_at,
        answers=[
            {
                "id": answer.id,
                "body": answer.body,
                "author_id": answer.author_id,
                "author": author_map[answer.author_id],
                "upvotes": answer.upvotes,
                "downvotes": answer.downvotes,
                "score": answer.score,
                "viewer_vote": answer_votes.get(answer.id),
                "created_at": answer.created_at,
                "comments": [
                    _comment_payload(
                        comment,
                        author=author_map[comment.author_id],
                        viewer_vote=comment_votes.get(comment.id),
                    )
                    for comment in answer_comments_map.get(answer.id, [])
                ],
                "related": [
                    link_summaries[link.id]
                    for link in answer_links_map.get(answer.id, [])
                    if link.id in link_summaries
                ],
            }
            for answer in answers
        ],
        comments=[
            _comment_payload(
                comment,
                author=author_map[comment.author_id],
                viewer_vote=comment_votes.get(comment.id),
            )
            for comment in q_comments
        ],
        related=[
            link_summaries[link.id]
            for link in question_links
            if link.id in link_summaries
        ],
    )
