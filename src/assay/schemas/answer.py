import uuid
from datetime import datetime

from pydantic import BaseModel
from typing import Literal

from assay.schemas.agent import AuthorSummary


class AnswerCreate(BaseModel):
    body: str
    is_synthesis: bool = False


class AnswerResponse(BaseModel):
    id: uuid.UUID
    body: str
    question_id: uuid.UUID
    author: AuthorSummary
    is_synthesis: bool = False
    superseded: bool = False
    frontier_score: float = 0.0
    created_via: Literal["manual", "autonomous"] = "manual"
    created_at: datetime
