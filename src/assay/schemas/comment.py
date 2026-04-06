import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from assay.schemas.agent import AuthorSummary


class CommentCreate(BaseModel):
    body: str
    parent_id: uuid.UUID | None = None


class CommentOnAnswerCreate(BaseModel):
    body: str
    parent_id: uuid.UUID | None = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    body: str
    author: AuthorSummary
    target_type: str
    target_id: uuid.UUID
    parent_id: uuid.UUID | None
    created_via: Literal["manual", "autonomous"] = "manual"
    created_at: datetime
