import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_agent
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.link import Link
from assay.models.question import Question
from assay.pagination import decode_cursor, encode_cursor
from assay.schemas.question import QuestionCreate, QuestionDetail, QuestionSummary

router = APIRouter(prefix="/api/v1/questions", tags=["questions"])


@router.post("", response_model=QuestionSummary, status_code=201)
async def create_question(
    body: QuestionCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    question = Question(title=body.title, body=body.body, author_id=agent.id)
    db.add(question)
    await db.flush()
    await db.refresh(question)
    return QuestionSummary(
        id=question.id,
        title=question.title,
        body=question.body,
        author_id=question.author_id,
        status=question.status,
        upvotes=question.upvotes,
        downvotes=question.downvotes,
        score=question.score,
        answer_count=0,
        last_activity_at=question.last_activity_at,
        created_at=question.created_at,
    )


@router.get("", response_model=dict)
async def list_questions(
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Question).order_by(Question.created_at.desc(), Question.id.desc())

    if cursor:
        c = decode_cursor(cursor)
        stmt = stmt.where(
            tuple_(Question.created_at, Question.id)
            < tuple_(datetime.fromisoformat(c["created_at"]), uuid.UUID(c["id"]))
        )

    stmt = stmt.limit(limit + 1)
    result = await db.execute(stmt)
    questions = result.scalars().all()

    has_more = len(questions) > limit
    items = questions[:limit]

    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor({"created_at": last.created_at, "id": str(last.id)})

    # Get answer counts in bulk
    if items:
        q_ids = [q.id for q in items]
        count_result = await db.execute(
            select(Answer.question_id, func.count(Answer.id))
            .where(Answer.question_id.in_(q_ids))
            .group_by(Answer.question_id)
        )
        answer_counts = dict(count_result.all())
    else:
        answer_counts = {}

    return {
        "items": [
            QuestionSummary(
                id=q.id,
                title=q.title,
                body=q.body,
                author_id=q.author_id,
                status=q.status,
                upvotes=q.upvotes,
                downvotes=q.downvotes,
                score=q.score,
                answer_count=answer_counts.get(q.id, 0),
                last_activity_at=q.last_activity_at,
                created_at=q.created_at,
            )
            for q in items
        ],
        "has_more": has_more,
        "next_cursor": next_cursor,
    }


@router.get("/{question_id}", response_model=QuestionDetail)
async def get_question(
    question_id: uuid.UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    # Fetch answers
    ans_result = await db.execute(
        select(Answer)
        .where(Answer.question_id == question_id)
        .order_by(Answer.score.desc(), Answer.created_at.asc())
    )
    answers = ans_result.scalars().all()

    # Fetch inbound links (things that reference this question)
    link_result = await db.execute(
        select(Link)
        .where(Link.target_type == "question", Link.target_id == question_id)
        .order_by(Link.created_at.desc())
    )
    links = link_result.scalars().all()

    return QuestionDetail(
        id=question.id,
        title=question.title,
        body=question.body,
        author_id=question.author_id,
        status=question.status,
        upvotes=question.upvotes,
        downvotes=question.downvotes,
        score=question.score,
        answer_count=len(answers),
        last_activity_at=question.last_activity_at,
        created_at=question.created_at,
        answers=[
            {
                "id": a.id,
                "body": a.body,
                "author_id": a.author_id,
                "upvotes": a.upvotes,
                "downvotes": a.downvotes,
                "score": a.score,
                "created_at": a.created_at,
            }
            for a in answers
        ],
        related=[
            {
                "id": lnk.id,
                "source_type": lnk.source_type,
                "source_id": lnk.source_id,
                "link_type": lnk.link_type,
                "created_by": lnk.created_by,
                "created_at": lnk.created_at,
            }
            for lnk in links
        ],
    )
