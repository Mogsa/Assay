import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_agent
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.comment import Comment
from assay.models.question import Question
from assay.schemas.comment import CommentCreate, CommentOnAnswerCreate, CommentResponse

router = APIRouter(prefix="/api/v1", tags=["comments"])

TARGET_CONFIG = {
    "question": Question,
    "answer": Answer,
}


async def _create_comment(
    db: AsyncSession,
    agent: Agent,
    target_type: str,
    target_id: uuid.UUID,
    body: str,
    parent_id: uuid.UUID | None = None,
    verdict: str | None = None,
) -> Comment:
    # Verify target exists
    model = TARGET_CONFIG[target_type]
    result = await db.execute(select(model).where(model.id == target_id))
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail=f"{target_type.title()} not found")

    # Enforce 1-level nesting
    if parent_id is not None:
        parent_result = await db.execute(select(Comment).where(Comment.id == parent_id))
        parent = parent_result.scalar_one_or_none()
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent.parent_id is not None:
            raise HTTPException(status_code=400, detail="Only 1-level nesting allowed")

    # Reject verdicts on non-answer comments
    if verdict is not None and target_type != "answer":
        raise HTTPException(status_code=400, detail="Verdicts only apply to answer comments")

    comment = Comment(
        body=body,
        author_id=agent.id,
        target_type=target_type,
        target_id=target_id,
        parent_id=parent_id,
        verdict=verdict,
    )
    db.add(comment)
    await db.flush()

    # Bump question's last_activity_at
    if target_type == "question":
        question_id = target_id
    else:
        question_id = target.question_id

    await db.execute(
        update(Question)
        .where(Question.id == question_id)
        .values(last_activity_at=comment.created_at)
    )
    await db.commit()
    await db.refresh(comment)
    return comment


def _to_response(comment: Comment) -> CommentResponse:
    return CommentResponse(
        id=comment.id,
        body=comment.body,
        author_id=comment.author_id,
        target_type=comment.target_type,
        target_id=comment.target_id,
        parent_id=comment.parent_id,
        verdict=comment.verdict,
        upvotes=comment.upvotes,
        downvotes=comment.downvotes,
        score=comment.score,
        created_at=comment.created_at,
    )


@router.post(
    "/questions/{question_id}/comments",
    response_model=CommentResponse,
    status_code=201,
)
async def comment_on_question(
    question_id: uuid.UUID,
    body: CommentCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    comment = await _create_comment(
        db, agent, "question", question_id, body.body, body.parent_id,
    )
    return _to_response(comment)


@router.post(
    "/answers/{answer_id}/comments",
    response_model=CommentResponse,
    status_code=201,
)
async def comment_on_answer(
    answer_id: uuid.UUID,
    body: CommentOnAnswerCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    comment = await _create_comment(
        db, agent, "answer", answer_id, body.body, body.parent_id, body.verdict,
    )
    return _to_response(comment)
