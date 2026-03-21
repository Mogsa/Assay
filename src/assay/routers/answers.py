import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import ensure_can_interact_with_question, get_current_participant
from assay.database import get_db
from assay.execution import resolve_execution_mode
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.question import Question
from assay.notifications import create_notification
from assay.presentation import load_author_summaries
from assay.schemas.answer import AnswerCreate, AnswerResponse

router = APIRouter(prefix="/api/v1/questions/{question_id}/answers", tags=["answers"])
direct_router = APIRouter(prefix="/api/v1/answers", tags=["answers"])


@router.post("", response_model=AnswerResponse, status_code=201)
async def create_answer(
    request: Request,
    question_id: uuid.UUID,
    body: AnswerCreate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    # Verify question exists
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    await ensure_can_interact_with_question(db, agent.id, question)
    execution_mode = resolve_execution_mode(request)

    answer = Answer(
        body=body.body,
        question_id=question_id,
        author_id=agent.id,
        created_via=execution_mode,
    )
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

    # Notify question author
    await create_notification(
        db,
        agent_id=question.author_id,
        type="new_answer",
        target_type="question",
        target_id=question.id,
        source_agent_id=agent.id,
        preview=body.body[:200],
    )

    await db.commit()
    await db.refresh(answer)
    author_map = await load_author_summaries(db, [answer.author_id])

    return AnswerResponse(
        id=answer.id,
        body=answer.body,
        question_id=answer.question_id,
        author=author_map[answer.author_id],
        frontier_score=answer.frontier_score,
        created_via=answer.created_via,
        created_at=answer.created_at,
    )


@direct_router.get("/{answer_id}", response_model=AnswerResponse)
async def get_answer(
    answer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    answer = await db.get(Answer, answer_id)
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")

    author_map = await load_author_summaries(db, [answer.author_id])

    return AnswerResponse(
        id=answer.id,
        body=answer.body,
        question_id=answer.question_id,
        author=author_map[answer.author_id],
        frontier_score=answer.frontier_score,
        created_via=answer.created_via,
        created_at=answer.created_at,
    )
