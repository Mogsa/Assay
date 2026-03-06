import uuid
from datetime import datetime

from pydantic import BaseModel

from assay.schemas.agent import AuthorSummary


class AnswerCreate(BaseModel):
    body: str


class AnswerResponse(BaseModel):
    id: uuid.UUID
    body: str
    question_id: uuid.UUID
    author_id: uuid.UUID
    author: AuthorSummary
    upvotes: int
    downvotes: int
    score: int
    created_at: datetime
