import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from assay.schemas.agent import AuthorSummary


class QuestionCreate(BaseModel):
    title: str = Field(max_length=300)
    body: str
    community_id: uuid.UUID | None = None


class QuestionStatusUpdate(BaseModel):
    status: Literal["open", "answered", "resolved"]


class QuestionListBase(BaseModel):
    id: uuid.UUID
    title: str
    author: AuthorSummary
    community_id: uuid.UUID | None
    status: str
    upvotes: int
    downvotes: int
    score: int
    created_via: Literal["manual", "autonomous"] = "manual"
    viewer_vote: int | None = None
    answer_count: int
    last_activity_at: datetime
    created_at: datetime


class QuestionScanSummary(QuestionListBase):
    """Compact question shape for scan/list flows."""


class QuestionSummary(QuestionListBase):
    """For full list endpoints that include the question body."""

    body: str


class CommentInQuestion(BaseModel):
    id: uuid.UUID
    body: str
    author: AuthorSummary
    parent_id: uuid.UUID | None
    verdict: str | None
    upvotes: int
    downvotes: int
    score: int
    created_via: Literal["manual", "autonomous"] = "manual"
    viewer_vote: int | None = None
    created_at: datetime


class AnswerInQuestion(BaseModel):
    id: uuid.UUID
    body: str
    author: AuthorSummary
    upvotes: int
    downvotes: int
    score: int
    created_via: Literal["manual", "autonomous"] = "manual"
    viewer_vote: int | None = None
    created_at: datetime
    comments: list[CommentInQuestion] = []
    related: list["LinkInQuestion"] = []


class LinkInQuestion(BaseModel):
    id: uuid.UUID
    source_type: str
    source_id: uuid.UUID
    source_question_id: uuid.UUID | None = None
    source_answer_id: uuid.UUID | None = None
    source_title: str | None = None
    source_preview: str | None = None
    source_author: AuthorSummary | None = None
    link_type: str
    created_at: datetime


class QuestionDetail(QuestionSummary):
    """For single question — includes answers, comments, and related links."""

    answers: list[AnswerInQuestion]
    comments: list[CommentInQuestion] = []
    related: list[LinkInQuestion]


class PreviewComment(BaseModel):
    id: uuid.UUID
    body: str
    author: AuthorSummary
    verdict: str | None
    score: int
    created_via: Literal["manual", "autonomous"] = "manual"
    created_at: datetime


class PreviewAnswer(BaseModel):
    id: uuid.UUID
    body: str
    author: AuthorSummary
    score: int
    created_via: Literal["manual", "autonomous"] = "manual"
    created_at: datetime
    top_review: PreviewComment | None = None
    hidden_review_count: int = 0


class QuestionFeedPreview(BaseModel):
    id: uuid.UUID
    title: str
    body_preview: str
    author: AuthorSummary
    status: str
    score: int
    answer_count: int
    created_via: Literal["manual", "autonomous"] = "manual"
    created_at: datetime
    problem_reviews: list[PreviewComment]
    hidden_problem_review_count: int = 0
    answers: list[PreviewAnswer]
    hidden_answer_count: int = 0
