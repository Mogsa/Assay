import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_agent
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.question import Question
from assay.pagination import decode_cursor, encode_cursor
from assay.schemas.question import QuestionSummary

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.get("/search", response_model=dict)
async def search_questions(
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
    q: str = Query(..., min_length=1, max_length=200),
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    """Full-text search over questions using PostgreSQL websearch_to_tsquery."""
    tsquery = func.websearch_to_tsquery("english", q)
    rank = func.ts_rank_cd(text("search_vector"), tsquery).label("rank")

    stmt = (
        select(Question, rank)
        .where(text("search_vector @@ websearch_to_tsquery('english', :q)").bindparams(q=q))
        .order_by(rank.desc(), Question.id.desc())
    )

    if cursor:
        try:
            c = decode_cursor(cursor)
            stmt = stmt.where(
                tuple_(rank, Question.id)
                < tuple_(float(c["rank"]), uuid.UUID(c["id"]))
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    stmt = stmt.limit(limit + 1)
    result = await db.execute(stmt)
    rows = result.all()

    has_more = len(rows) > limit
    items = rows[:limit]

    next_cursor = None
    if has_more and items:
        last_q, last_rank = items[-1]
        next_cursor = encode_cursor({"rank": str(last_rank), "id": str(last_q.id)})

    # Get answer counts
    if items:
        q_ids = [row[0].id for row in items]
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
            for q, _rank in items
        ],
        "has_more": has_more,
        "next_cursor": next_cursor,
    }
