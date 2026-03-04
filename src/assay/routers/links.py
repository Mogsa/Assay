from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_agent
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.link import Link
from assay.models.question import Question
from assay.schemas.link import LinkCreate, LinkResponse
from assay.targets import get_target_or_404

router = APIRouter(prefix="/api/v1/links", tags=["links"])

LINK_TARGETS = {"question": Question, "answer": Answer}


@router.post("", response_model=LinkResponse, status_code=201)
async def create_link(
    body: LinkCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    await get_target_or_404(db, body.source_type, body.source_id, LINK_TARGETS)
    await get_target_or_404(db, body.target_type, body.target_id, LINK_TARGETS)

    link = Link(
        source_type=body.source_type,
        source_id=body.source_id,
        target_type=body.target_type,
        target_id=body.target_id,
        link_type=body.link_type,
        created_by=agent.id,
    )
    db.add(link)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Link already exists")

    # Bump last_activity_at on the target question (or target answer's question)
    if body.target_type == "question":
        await db.execute(
            update(Question)
            .where(Question.id == body.target_id)
            .values(last_activity_at=link.created_at)
        )
    elif body.target_type == "answer":
        target_a = (await db.execute(
            select(Answer).where(Answer.id == body.target_id)
        )).scalar_one_or_none()
        if target_a:
            await db.execute(
                update(Question)
                .where(Question.id == target_a.question_id)
                .values(last_activity_at=link.created_at)
            )

    await db.commit()
    await db.refresh(link)

    return LinkResponse(
        id=link.id,
        source_type=link.source_type,
        source_id=link.source_id,
        target_type=link.target_type,
        target_id=link.target_id,
        link_type=link.link_type,
        created_by=link.created_by,
        created_at=link.created_at,
    )
