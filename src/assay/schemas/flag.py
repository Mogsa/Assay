import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FlagCreate(BaseModel):
    target_type: Literal["question", "answer", "comment"]
    target_id: uuid.UUID
    reason: Literal["spam", "offensive", "off_topic", "duplicate", "other"]
    detail: str | None = Field(None, max_length=500)


class FlagResponse(BaseModel):
    id: uuid.UUID
    flagger_id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    reason: str
    detail: str | None
    status: str
    created_at: datetime


class FlagResolve(BaseModel):
    status: Literal["resolved", "dismissed"]
