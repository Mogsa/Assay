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
    verdict: Literal["correct", "incorrect", "partially_correct", "unsure"] | None = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    body: str
    author_id: uuid.UUID
    author: AuthorSummary
    target_type: str
    target_id: uuid.UUID
    parent_id: uuid.UUID | None
    verdict: str | None
    upvotes: int
    downvotes: int
    score: int
    created_at: datetime
