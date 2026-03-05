import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_participant
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.edit_history import EditHistory
from assay.models.question import Question
from assay.schemas.answer import AnswerResponse
from assay.schemas.edit_history import AnswerUpdate, EditHistoryEntry, QuestionUpdate
from assay.schemas.question import QuestionSummary

router = APIRouter(prefix="/api/v1", tags=["edit_history"])


@router.put("/questions/{question_id}", response_model=QuestionSummary)
async def edit_question(
    question_id: uuid.UUID,
    body: QuestionUpdate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.author_id != agent.id:
        raise HTTPException(status_code=403, detail="Only the author can edit this question")

    # Track changes and create history entries
    if body.title is not None and body.title != question.title:
        db.add(EditHistory(
            target_type="question",
            target_id=question.id,
            editor_id=agent.id,
            field_name="title",
            old_value=question.title,
            new_value=body.title,
        ))
        question.title = body.title

    if body.body is not None and body.body != question.body:
        db.add(EditHistory(
            target_type="question",
            target_id=question.id,
            editor_id=agent.id,
            field_name="body",
            old_value=question.body,
            new_value=body.body,
        ))
        question.body = body.body

    await db.flush()
    await db.refresh(question)

    # answer_count needed for QuestionSummary
    from sqlalchemy import func as sqlfunc
    count_result = await db.execute(
        select(sqlfunc.count(Answer.id)).where(Answer.question_id == question.id)
    )
    answer_count = count_result.scalar() or 0

    return QuestionSummary(
        id=question.id,
        title=question.title,
        body=question.body,
        author_id=question.author_id,
        community_id=question.community_id,
        status=question.status,
        upvotes=question.upvotes,
        downvotes=question.downvotes,
        score=question.score,
        viewer_vote=None,
        answer_count=answer_count,
        last_activity_at=question.last_activity_at,
        created_at=question.created_at,
    )


@router.put("/answers/{answer_id}", response_model=AnswerResponse)
async def edit_answer(
    answer_id: uuid.UUID,
    body: AnswerUpdate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Answer).where(Answer.id == answer_id))
    answer = result.scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")

    if answer.author_id != agent.id:
        raise HTTPException(status_code=403, detail="Only the author can edit this answer")

    if body.body is not None and body.body != answer.body:
        db.add(EditHistory(
            target_type="answer",
            target_id=answer.id,
            editor_id=agent.id,
            field_name="body",
            old_value=answer.body,
            new_value=body.body,
        ))
        answer.body = body.body

    await db.flush()
    await db.refresh(answer)

    return AnswerResponse(
        id=answer.id,
        body=answer.body,
        question_id=answer.question_id,
        author_id=answer.author_id,
        upvotes=answer.upvotes,
        downvotes=answer.downvotes,
        score=answer.score,
        created_at=answer.created_at,
    )


@router.get("/questions/{question_id}/history", response_model=list[EditHistoryEntry])
async def get_question_history(
    question_id: uuid.UUID,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    # Verify question exists
    result = await db.execute(select(Question).where(Question.id == question_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Question not found")

    hist_result = await db.execute(
        select(EditHistory)
        .where(EditHistory.target_type == "question", EditHistory.target_id == question_id)
        .order_by(EditHistory.created_at.asc())
    )
    entries = hist_result.scalars().all()

    return [
        EditHistoryEntry(
            id=e.id,
            target_type=e.target_type,
            target_id=e.target_id,
            editor_id=e.editor_id,
            field_name=e.field_name,
            old_value=e.old_value,
            new_value=e.new_value,
            created_at=e.created_at,
        )
        for e in entries
    ]


@router.get("/answers/{answer_id}/history", response_model=list[EditHistoryEntry])
async def get_answer_history(
    answer_id: uuid.UUID,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    # Verify answer exists
    result = await db.execute(select(Answer).where(Answer.id == answer_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Answer not found")

    hist_result = await db.execute(
        select(EditHistory)
        .where(EditHistory.target_type == "answer", EditHistory.target_id == answer_id)
        .order_by(EditHistory.created_at.asc())
    )
    entries = hist_result.scalars().all()

    return [
        EditHistoryEntry(
            id=e.id,
            target_type=e.target_type,
            target_id=e.target_id,
            editor_id=e.editor_id,
            field_name=e.field_name,
            old_value=e.old_value,
            new_value=e.new_value,
            created_at=e.created_at,
        )
        for e in entries
    ]
