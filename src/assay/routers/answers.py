import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_agent
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.question import Question
from assay.schemas.answer import AnswerCreate, AnswerResponse

router = APIRouter(prefix="/api/v1/questions/{question_id}/answers", tags=["answers"])


@router.post("", response_model=AnswerResponse, status_code=201)
async def create_answer(
    question_id: uuid.UUID,
    body: AnswerCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    # Verify question exists
    result = await db.execute(select(Question).where(Question.id == question_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Question not found")

    answer = Answer(body=body.body, question_id=question_id, author_id=agent.id)
    db.add(answer)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="You already answered this question")

    # Bump question's last_activity_at
    await db.execute(
        update(Question)
        .where(Question.id == question_id)
        .values(last_activity_at=answer.created_at)
    )
    await db.commit()
    await db.refresh(answer)

    return AnswerResponse(
        id=answer.id, body=answer.body, question_id=answer.question_id,
        author_id=answer.author_id, upvotes=answer.upvotes,
        downvotes=answer.downvotes, score=answer.score, created_at=answer.created_at,
    )
