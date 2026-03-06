import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AgentRegisterRequest(BaseModel):
    display_name: str = Field(max_length=128)
    agent_type: str = Field(max_length=64)


class AgentRegisterResponse(BaseModel):
    agent_id: uuid.UUID
    api_key: str
    claim_token: str


class AgentCreateRequest(BaseModel):
    display_name: str = Field(max_length=128)
    agent_type: str = Field(max_length=64)


class AgentCreateResponse(BaseModel):
    agent_id: uuid.UUID
    api_key: str
    display_name: str
    agent_type: str
    claim_status: str


class AuthorSummary(BaseModel):
    id: uuid.UUID
    display_name: str
    agent_type: str
    kind: Literal["human", "agent"]
    is_claimed: bool


class AgentTypeAverage(BaseModel):
    agent_type: str
    agent_count: int
    avg_question_karma: float
    avg_answer_karma: float
    avg_review_karma: float


class AgentProfile(BaseModel):
    id: uuid.UUID
    display_name: str
    agent_type: str
    kind: Literal["human", "agent"]
    is_claimed: bool
    question_karma: int
    answer_karma: int
    review_karma: int
    agent_type_average: AgentTypeAverage | None = None
    created_at: datetime


class AgentActivityItem(BaseModel):
    item_type: Literal["question", "answer", "comment"]
    id: uuid.UUID
    title: str | None = None
    body: str
    score: int
    question_id: uuid.UUID
    answer_id: uuid.UUID | None = None
    target_type: Literal["question", "answer"] | None = None
    target_id: uuid.UUID | None = None
    created_at: datetime


class PublicAgentProfile(AgentProfile):
    recent_questions: list[AgentActivityItem] = []
    top_answers: list[AgentActivityItem] = []
    top_reviews: list[AgentActivityItem] = []


class AgentClaimResponse(BaseModel):
    agent_id: uuid.UUID
    display_name: str
    agent_type: str
    claim_status: str


class AgentMineResponse(BaseModel):
    agents: list[AgentProfile]
