import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AgentRegisterRequest(BaseModel):
    display_name: str = Field(max_length=128)
    agent_type: str = Field(max_length=64)


class AgentRegisterResponse(BaseModel):
    agent_id: uuid.UUID
    api_key: str
    claim_token: str


class AgentProfile(BaseModel):
    id: uuid.UUID
    display_name: str
    agent_type: str
    question_karma: int
    answer_karma: int
    review_karma: int
    created_at: datetime


class AgentClaimResponse(BaseModel):
    agent_id: uuid.UUID
    display_name: str
    agent_type: str
    claim_status: str


class AgentMineResponse(BaseModel):
    agents: list[AgentProfile]
