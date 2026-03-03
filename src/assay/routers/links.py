from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_agent
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.link import Link
from assay.schemas.link import LinkCreate, LinkResponse

router = APIRouter(prefix="/api/v1/links", tags=["links"])


@router.post("", response_model=LinkResponse, status_code=201)
async def create_link(
    body: LinkCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
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
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Link already exists")
    await db.refresh(link)

    return LinkResponse(
        id=link.id, source_type=link.source_type, source_id=link.source_id,
        target_type=link.target_type, target_id=link.target_id,
        link_type=link.link_type, created_by=link.created_by,
        created_at=link.created_at,
    )
