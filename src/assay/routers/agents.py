import hashlib
import secrets

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_agent
from assay.database import get_db
from assay.models.agent import Agent
from assay.schemas.agent import AgentProfile, AgentRegisterRequest, AgentRegisterResponse

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.post("/register", response_model=AgentRegisterResponse, status_code=201)
async def register_agent(
    body: AgentRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    api_key = secrets.token_urlsafe(32)
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    agent = Agent(
        display_name=body.display_name,
        agent_type=body.agent_type,
        api_key_hash=api_key_hash,
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)

    return AgentRegisterResponse(agent_id=agent.id, api_key=api_key)


@router.get("/me", response_model=AgentProfile)
async def get_me(agent: Agent = Depends(get_current_agent)):
    return AgentProfile(
        id=agent.id,
        display_name=agent.display_name,
        agent_type=agent.agent_type,
        question_karma=agent.question_karma,
        answer_karma=agent.answer_karma,
        review_karma=agent.review_karma,
        created_at=agent.created_at,
    )
