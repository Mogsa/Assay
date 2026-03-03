import uuid
from datetime import datetime

from pydantic import BaseModel


class AnswerCreate(BaseModel):
    body: str


class AnswerResponse(BaseModel):
    id: uuid.UUID
    body: str
    question_id: uuid.UUID
    author_id: uuid.UUID
    upvotes: int
    downvotes: int
    score: int
    created_at: datetime
