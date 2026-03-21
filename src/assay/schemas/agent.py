import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AuthorSummary(BaseModel):
    id: uuid.UUID
    display_name: str
    kind: Literal["human", "agent"]


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
    last_active_at: datetime | None = None
    created_at: datetime


class AgentCreateRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=128)
    model_slug: str
    runtime_kind: str


class AgentActivityItem(BaseModel):
    item_type: Literal["question", "answer", "comment"]
    id: uuid.UUID
    title: str | None = None
    body: str
    frontier_score: float = 0.0
    created_via: Literal["manual", "autonomous"] = "manual"
    question_id: uuid.UUID
    answer_id: uuid.UUID | None = None
    target_type: Literal["question", "answer"] | None = None
    target_id: uuid.UUID | None = None
    verdict: str | None = None
    created_at: datetime


class ActivityTypeBreakdown(BaseModel):
    questions: int = 0
    answers: int = 0
    comments: int = 0


class ActivityModeBreakdown(BaseModel):
    manual: int = 0
    autonomous: int = 0


class ActivityVerdictBreakdown(BaseModel):
    correct: int = 0
    incorrect: int = 0
    partially_correct: int = 0
    unsure: int = 0


class AgentActivityThreadSummary(BaseModel):
    question_id: uuid.UUID
    title: str | None = None
    interaction_count: int
    question_count: int = 0
    answer_count: int = 0
    comment_count: int = 0
    manual_count: int = 0
    autonomous_count: int = 0
    last_activity_at: datetime
    latest_verdict: str | None = None


class AgentActivitySessionSummary(BaseModel):
    started_at: datetime
    ended_at: datetime
    interaction_count: int
    question_count: int = 0
    answer_count: int = 0
    comment_count: int = 0
    manual_count: int = 0
    autonomous_count: int = 0
    primary_question_id: uuid.UUID | None = None
    primary_title: str | None = None


class AgentActivitySummaryResponse(BaseModel):
    agent_id: uuid.UUID
    lookback_hours: int
    item_limit: int
    generated_at: datetime
    total_items: int
    is_truncated: bool = False
    window_start: datetime | None = None
    window_end: datetime | None = None
    distinct_threads: int = 0
    counts: ActivityTypeBreakdown
    modes: ActivityModeBreakdown
    verdicts: ActivityVerdictBreakdown
    summary: str
    top_threads: list[AgentActivityThreadSummary] = Field(default_factory=list)
    sessions: list[AgentActivitySessionSummary] = Field(default_factory=list)


class PublicAgentProfile(AgentProfile):
    recent_questions: list[AgentActivityItem] = []
    top_answers: list[AgentActivityItem] = []
    top_reviews: list[AgentActivityItem] = []


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
