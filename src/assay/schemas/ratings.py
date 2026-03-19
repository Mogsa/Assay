"""Schemas for R/N/G rating endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class RatingCreate(BaseModel):
    target_type: str
    target_id: uuid.UUID
    rigour: int
    novelty: int
    generativity: int
    reasoning: str | None = None

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, v: str) -> str:
        if v not in ("question", "answer", "comment"):
            raise ValueError("target_type must be question, answer, or comment")
        return v

    @field_validator("rigour", "novelty", "generativity")
    @classmethod
    def validate_score(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("scores must be between 1 and 5")
        return v


class RatingResponse(BaseModel):
    id: uuid.UUID
    rater_id: uuid.UUID
    rater_name: str
    target_type: str
    target_id: uuid.UUID
    rigour: int
    novelty: int
    generativity: int
    reasoning: str | None
    is_human: bool
    created_at: datetime


class RatingConsensus(BaseModel):
    rigour: float
    novelty: float
    generativity: float


class RatingsForItem(BaseModel):
    ratings: list[RatingResponse]
    consensus: RatingConsensus
    human_rating: RatingResponse | None
    frontier_score: float


class CalibrationAxis(BaseModel):
    mean_error: float
    n_items: int


class CalibrationResponse(BaseModel):
    rigour: CalibrationAxis
    novelty: CalibrationAxis
    generativity: CalibrationAxis
    per_agent: list[dict]
