import hashlib

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.database import get_db
from assay.models.agent import Agent

security = HTTPBearer()


async def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db),
) -> Agent:
    api_key_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    result = await db.execute(select(Agent).where(Agent.api_key_hash == api_key_hash))
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return agent
