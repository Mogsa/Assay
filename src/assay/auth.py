import hashlib
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.database import get_db
from assay.models.agent import Agent
from assay.models.community_member import CommunityMember
from assay.models.question import Question
from assay.models.session import Session

optional_bearer = HTTPBearer(auto_error=False)


async def _get_agent_from_bearer(
    credentials: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> Agent | None:
    if credentials is None:
        return None

    api_key_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    result = await db.execute(select(Agent).where(Agent.api_key_hash == api_key_hash))
    return result.scalar_one_or_none()


async def _get_agent_from_session(request: Request, db: AsyncSession) -> Agent | None:
    session_token = request.cookies.get("session")
    if not session_token:
        return None

    session_hash = hashlib.sha256(session_token.encode()).hexdigest()
    result = await db.execute(select(Session).where(Session.id == session_hash))
    session = result.scalar_one_or_none()
    if session is None or session.expires_at <= datetime.now(timezone.utc):
        return None

    agent_result = await db.execute(select(Agent).where(Agent.id == session.agent_id))
    return agent_result.scalar_one_or_none()


async def get_current_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> Agent:
    agent = await get_optional_principal(request, credentials, db)
    if agent is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return agent


async def get_optional_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> Agent | None:
    if credentials is not None:
        agent = await _get_agent_from_bearer(credentials, db)
        if agent is None:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return agent

    return await _get_agent_from_session(request, db)


async def get_current_human(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> Agent:
    if credentials is not None:
        agent = await _get_agent_from_bearer(credentials, db)
        if agent is None:
            raise HTTPException(status_code=401, detail="Invalid API key")
        raise HTTPException(status_code=403, detail="Human session required")

    agent = await _get_agent_from_session(request, db)
    if agent is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if agent.agent_type != "human":
        raise HTTPException(status_code=403, detail="Human session required")
    return agent


async def get_current_participant(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> Agent:
    if credentials is not None:
        agent = await _get_agent_from_bearer(credentials, db)
        if agent is None:
            raise HTTPException(status_code=401, detail="Invalid API key")
        if agent.claim_status != "claimed":
            raise HTTPException(
                status_code=403,
                detail="Agent must be claimed before participating",
            )
        return agent

    agent = await _get_agent_from_session(request, db)
    if agent is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return agent


async def ensure_can_interact_with_question(
    db: AsyncSession,
    actor_id,
    question: Question,
) -> None:
    if question.community_id is None:
        return

    membership = await db.execute(
        select(CommunityMember).where(
            CommunityMember.community_id == question.community_id,
            CommunityMember.agent_id == actor_id,
        )
    )
    if membership.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Not a member of this community")
