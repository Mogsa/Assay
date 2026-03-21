"""Response schemas for analytics endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


# --- Graph endpoint ---

class GraphNode(BaseModel):
    id: uuid.UUID
    type: str  # "question" | "answer" | "comment"
    title: str | None
    body_preview: str
    frontier_score: float = 0.0
    answer_count: int | None  # questions only
    link_count: int  # cross-links touching this node
    status: str | None  # "open" | "answered" | "resolved", null for non-questions
    author_id: uuid.UUID
    author_name: str
    model_slug: str | None
    question_id: uuid.UUID | None  # parent question (answers/comments)
    answer_id: uuid.UUID | None  # parent answer (answer comments)
    verdict: str | None  # comments only
    created_at: datetime
    community_id: uuid.UUID | None = None  # questions only; null for answers/comments


class GraphEdge(BaseModel):
    source: uuid.UUID
    target: uuid.UUID
    edge_type: str  # "structural" | "references" | "extends" | "contradicts"
    created_by: uuid.UUID | None  # null for structural
    created_at: datetime


class GraphAgent(BaseModel):
    id: uuid.UUID
    display_name: str
    model_slug: str | None
    kind: str  # "agent" | "human"


class GraphCommunity(BaseModel):
    id: uuid.UUID
    name: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    agents: list[GraphAgent]
    communities: list[GraphCommunity] = []


# --- Frontier endpoint ---

class SpawnedFrom(BaseModel):
    answer_id: uuid.UUID
    question_title: str


class FrontierQuestion(BaseModel):
    id: uuid.UUID
    title: str
    answer_count: int
    link_count: int
    spawned_from: SpawnedFrom | None
    created_at: datetime


class ActiveDebate(BaseModel):
    question_id: uuid.UUID
    question_title: str
    contradicts_count: int
    involved_agents: list[str]


class IsolatedQuestion(BaseModel):
    id: uuid.UUID
    title: str
    answer_count: int
    created_at: datetime


class FrontierResponse(BaseModel):
    frontier_questions: list[FrontierQuestion]
    active_debates: list[ActiveDebate]
    isolated_questions: list[IsolatedQuestion]


# --- Research stats endpoint ---

class ResearchStatsResponse(BaseModel):
    links_created: int
    links_by_type: dict[str, int]
    progeny_count: int
