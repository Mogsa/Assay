import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class AgentRegisterRequest(BaseModel):
    display_name: str = Field(max_length=128)
    agent_type: str | None = Field(default=None, max_length=64)
    description: str | None = Field(default=None, max_length=512)
    provider: str | None = Field(default=None, max_length=64)
    model_name: str | None = Field(default=None, max_length=128)
    runtime_kind: str | None = Field(default=None, max_length=64)

    @model_validator(mode="after")
    def validate_model_identity(self):
        if self.agent_type:
            return self
        required = [self.provider, self.model_name, self.runtime_kind]
        if all(required):
            return self
        raise ValueError("Provide agent_type or provider/model_name/runtime_kind")


class AgentRegisterResponse(BaseModel):
    agent_id: uuid.UUID
    api_key: str
    claim_url: str
    profile_url: str
    status: Literal["pending_claim"]


class AgentCreateRequest(BaseModel):
    display_name: str = Field(max_length=128)
    agent_type: str = Field(max_length=64)
    description: str | None = Field(default=None, max_length=512)
    provider: str | None = Field(default=None, max_length=64)
    model_name: str | None = Field(default=None, max_length=128)
    runtime_kind: str | None = Field(default=None, max_length=64)


class AgentCreateResponse(BaseModel):
    agent_id: uuid.UUID
    api_key: str
    display_name: str
    agent_type: str
    description: str | None = None
    provider: str | None = None
    model_name: str | None = None
    runtime_kind: str | None = None
    claim_status: str


class AuthorSummary(BaseModel):
    id: uuid.UUID
    display_name: str
    agent_type: str
    provider: str | None = None
    model_name: str | None = None
    runtime_kind: str | None = None
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
    description: str | None = None
    provider: str | None = None
    model_name: str | None = None
    runtime_kind: str | None = None
    kind: Literal["human", "agent"]
    is_claimed: bool
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
    provider: str | None = None
    model_name: str | None = None
    runtime_kind: str | None = None
    claim_status: str


class AgentMineResponse(BaseModel):
    agents: list[AgentProfile]


class AgentStatusResponse(BaseModel):
    agent_id: uuid.UUID
    display_name: str
    agent_type: str
    description: str | None = None
    provider: str | None = None
    model_name: str | None = None
    runtime_kind: str | None = None
    claim_status: str
    can_participate: bool
    profile_url: str
