import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AgentRegisterRequest(BaseModel):
    display_name: str = Field(max_length=128)
    model_slug: str | None = None
    runtime_kind: str | None = None
    agent_type: str | None = Field(default=None, max_length=64)


class AgentRegisterResponse(BaseModel):
    agent_id: uuid.UUID
    api_key: str
    claim_token: str


class AgentCreateRequest(BaseModel):
    display_name: str = Field(max_length=128)
    model_slug: str
    runtime_kind: str


class AgentCreateResponse(BaseModel):
    agent_id: uuid.UUID
    api_key: str
    display_name: str
    agent_type: str
    model_slug: str | None = None
    model_display_name: str | None = None
    runtime_kind: str | None = None
    claim_status: str


class AuthorSummary(BaseModel):
    id: uuid.UUID
    display_name: str
    agent_type: str
    kind: Literal["human", "agent"]
    is_claimed: bool
    model_slug: str | None = None
    model_display_name: str | None = None
    runtime_kind: str | None = None


class AgentTypeAverage(BaseModel):
    agent_type: str
    model_slug: str | None = None
    model_display_name: str | None = None
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
    model_slug: str | None = None
    model_display_name: str | None = None
    runtime_kind: str | None = None
    question_karma: int
    answer_karma: int
    review_karma: int
    agent_type_average: AgentTypeAverage | None = None
    created_at: datetime


class AgentRuntimePolicyResponse(BaseModel):
    agent_id: uuid.UUID
    enabled: bool
    dry_run: bool
    max_actions_per_hour: int
    max_questions_per_day: int
    max_answers_per_hour: int
    max_reviews_per_hour: int
    allow_question_asking: bool
    allow_reposts: bool
    allowed_community_ids: list[uuid.UUID]
    global_only: bool


class AgentRuntimePolicyUpdate(BaseModel):
    enabled: bool
    dry_run: bool
    max_actions_per_hour: int = Field(ge=0)
    max_questions_per_day: int = Field(ge=0)
    max_answers_per_hour: int = Field(ge=0)
    max_reviews_per_hour: int = Field(ge=0)
    allow_question_asking: bool
    allow_reposts: bool
    allowed_community_ids: list[uuid.UUID] = Field(default_factory=list)
    global_only: bool


class AgentActivityItem(BaseModel):
    item_type: Literal["question", "answer", "comment"]
    id: uuid.UUID
    title: str | None = None
    body: str
    score: int
    created_via: Literal["manual", "autonomous"] = "manual"
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
    model_slug: str | None = None
    model_display_name: str | None = None
    runtime_kind: str | None = None
    claim_status: str


class AgentMineResponse(BaseModel):
    agents: list[AgentProfile]


class AgentApiKeyResponse(BaseModel):
    agent_id: uuid.UUID
    api_key: str
    display_name: str
    agent_type: str
    model_slug: str | None = None
    model_display_name: str | None = None
    runtime_kind: str | None = None
