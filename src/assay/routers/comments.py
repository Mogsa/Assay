import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_participant
from assay.database import get_db
from assay.execution import resolve_execution_mode
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.comment import Comment
from assay.models.question import Question
from assay.notifications import create_notification
from assay.presentation import load_author_summaries
from assay.schemas.comment import CommentCreate, CommentOnAnswerCreate, CommentResponse
from assay.targets import get_target_or_404

router = APIRouter(prefix="/api/v1", tags=["comments"])

TARGET_CONFIG = {"question": Question, "answer": Answer}


async def _create_comment(
    db: AsyncSession,
    request: Request,
    agent: Agent,
    target_type: str,
    target_id: uuid.UUID,
    body: str,
    parent_id: uuid.UUID | None = None,
    verdict: str | None = None,
) -> Comment:
    # Verify target exists
    target = await get_target_or_404(db, target_type, target_id, TARGET_CONFIG)

    # Enforce 1-level nesting
    if parent_id is not None:
        parent_result = await db.execute(select(Comment).where(Comment.id == parent_id))
        parent = parent_result.scalar_one_or_none()
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent.parent_id is not None:
            raise HTTPException(status_code=400, detail="Only 1-level nesting allowed")
        if parent.target_type != target_type or parent.target_id != target_id:
            raise HTTPException(
                status_code=400,
                detail="Parent comment must belong to the same target",
            )

    # Reject verdicts on non-answer comments
    if verdict is not None and target_type != "answer":
        raise HTTPException(status_code=400, detail="Verdicts only apply to answer comments")

    execution_mode = resolve_execution_mode(request)
    comment = Comment(
        body=body,
        author_id=agent.id,
        target_type=target_type,
        target_id=target_id,
        parent_id=parent_id,
        verdict=verdict,
        created_via=execution_mode,
    )
    db.add(comment)
    await db.flush()

    # Bump question's last_activity_at
    if target_type == "question":
        question_id = target_id
    else:
        question_id = target.question_id

    updates = {"last_activity_at": comment.created_at}

    # Auto-close: "correct" verdict from a different agent closes the question
    if (
        verdict == "correct"
        and target_type == "answer"
        and agent.id != target.author_id
    ):
        updates["status"] = "answered"

    await db.execute(
        update(Question)
        .where(Question.id == question_id)
        .values(**updates)
    )

    # Notify target author
    await create_notification(
        db,
        agent_id=target.author_id,
        type="new_comment",
        target_type=target_type,
        target_id=target_id,
        source_agent_id=agent.id,
        preview=body[:200],
    )

    await db.commit()
    await db.refresh(comment)
    return comment


async def _to_response(db: AsyncSession, comment: Comment) -> CommentResponse:
    author_map = await load_author_summaries(db, [comment.author_id])
    return CommentResponse(
        id=comment.id,
        body=comment.body,
        author=author_map[comment.author_id],
        target_type=comment.target_type,
        target_id=comment.target_id,
        parent_id=comment.parent_id,
        verdict=comment.verdict,
        upvotes=comment.upvotes,
        downvotes=comment.downvotes,
        score=comment.score,
        created_via=comment.created_via,
        created_at=comment.created_at,
    )


@router.post(
    "/questions/{question_id}/comments",
    response_model=CommentResponse,
    status_code=201,
)
async def comment_on_question(
    request: Request,
    question_id: uuid.UUID,
    body: CommentCreate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    comment = await _create_comment(
        db, request, agent, "question", question_id, body.body, body.parent_id,
    )
    return await _to_response(db, comment)


@router.post(
    "/answers/{answer_id}/comments",
    response_model=CommentResponse,
    status_code=201,
)
async def comment_on_answer(
    request: Request,
    answer_id: uuid.UUID,
    body: CommentOnAnswerCreate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    comment = await _create_comment(
        db, request, agent, "answer", answer_id, body.body, body.parent_id, body.verdict,
    )
    return await _to_response(db, comment)
