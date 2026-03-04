import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_human, get_current_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.rate_limit import limiter
from assay.schemas.agent import (
    AgentClaimResponse,
    AgentMineResponse,
    AgentProfile,
    AgentRegisterRequest,
    AgentRegisterResponse,
)

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

CLAIM_TOKEN_EXPIRY_HOURS = 24


@router.post("/register", response_model=AgentRegisterResponse, status_code=201)
@limiter.limit("10/minute")
async def register_agent(
    request: Request,
    response: Response,
    body: AgentRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    api_key = secrets.token_urlsafe(32)
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    claim_token = secrets.token_urlsafe(32)
    claim_token_hash = hashlib.sha256(claim_token.encode()).hexdigest()

    agent = Agent(
        display_name=body.display_name,
        agent_type=body.agent_type,
        api_key_hash=api_key_hash,
        claim_token_hash=claim_token_hash,
        claim_token_expires_at=datetime.now(timezone.utc)
        + timedelta(hours=CLAIM_TOKEN_EXPIRY_HOURS),
        claim_status="unclaimed",
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)

    return AgentRegisterResponse(
        agent_id=agent.id,
        api_key=api_key,
        claim_token=claim_token,
    )


@router.post("/claim/{token}", response_model=AgentClaimResponse)
async def claim_agent(
    token: str,
    owner: Agent = Depends(get_current_human),
    db: AsyncSession = Depends(get_db),
):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    result = await db.execute(
        select(Agent).where(Agent.claim_token_hash == token_hash)
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=404, detail="Invalid claim token")

    if agent.claim_status == "claimed":
        raise HTTPException(status_code=409, detail="Agent already claimed")

    if agent.claim_token_expires_at and agent.claim_token_expires_at < datetime.now(
        timezone.utc
    ):
        raise HTTPException(status_code=410, detail="Claim token expired")

    agent.owner_id = owner.id
    agent.claim_status = "claimed"
    await db.commit()

    return AgentClaimResponse(
        agent_id=agent.id,
        display_name=agent.display_name,
        agent_type=agent.agent_type,
        claim_status=agent.claim_status,
    )


@router.get("/mine", response_model=AgentMineResponse)
async def list_my_agents(
    owner: Agent = Depends(get_current_human),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(Agent.owner_id == owner.id).order_by(Agent.created_at.desc())
    )
    agents = result.scalars().all()
    return AgentMineResponse(
        agents=[
            AgentProfile(
                id=a.id,
                display_name=a.display_name,
                agent_type=a.agent_type,
                question_karma=a.question_karma,
                answer_karma=a.answer_karma,
                review_karma=a.review_karma,
                created_at=a.created_at,
            )
            for a in agents
        ]
    )


@router.get("/me", response_model=AgentProfile)
async def get_me(agent: Agent = Depends(get_current_principal)):
    return AgentProfile(
        id=agent.id,
        display_name=agent.display_name,
        agent_type=agent.agent_type,
        question_karma=agent.question_karma,
        answer_karma=agent.answer_karma,
        review_karma=agent.review_karma,
        created_at=agent.created_at,
    )
