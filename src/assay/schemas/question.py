import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    title: str = Field(max_length=300)
    body: str
    community_id: uuid.UUID | None = None


class QuestionSummary(BaseModel):
    """For list endpoints — no nested answers."""

    id: uuid.UUID
    title: str
    body: str
    author_id: uuid.UUID
    community_id: uuid.UUID | None
    status: str
    upvotes: int
    downvotes: int
    score: int
    answer_count: int
    last_activity_at: datetime
    created_at: datetime


class CommentInQuestion(BaseModel):
    id: uuid.UUID
    body: str
    author_id: uuid.UUID
    parent_id: uuid.UUID | None
    verdict: str | None
    upvotes: int
    downvotes: int
    score: int
    created_at: datetime


class AnswerInQuestion(BaseModel):
    id: uuid.UUID
    body: str
    author_id: uuid.UUID
    upvotes: int
    downvotes: int
    score: int
    created_at: datetime
    comments: list[CommentInQuestion] = []


class LinkInQuestion(BaseModel):
    id: uuid.UUID
    source_type: str
    source_id: uuid.UUID
    link_type: str
    created_by: uuid.UUID
    created_at: datetime


class QuestionDetail(QuestionSummary):
    """For single question — includes answers, comments, and related links."""

    answers: list[AnswerInQuestion]
    comments: list[CommentInQuestion] = []
    related: list[LinkInQuestion]
