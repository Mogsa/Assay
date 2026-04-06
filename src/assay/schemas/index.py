"""Response schemas for the thread index endpoint."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class ThreadSummary(BaseModel):
    root_question_id: uuid.UUID
    root_title: str
    community_id: uuid.UUID | None
    depth: int
    node_count: int
    contradicts_count: int
    avg_frontier_score: float
    has_synthesis: bool
    last_activity_at: datetime
    top_contributors: list[str]


class IndexResponse(BaseModel):
    threads: list[ThreadSummary]
    standalone_count: int
