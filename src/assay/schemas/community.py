import re
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class CommunityCreate(BaseModel):
    name: str = Field(max_length=64)
    display_name: str = Field(max_length=128)
    description: str

    @field_validator("name")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not SLUG_PATTERN.match(v):
            msg = "Must be a lowercase slug (e.g. 'machine-learning')"
            raise ValueError(msg)
        return v


class CommunityResponse(BaseModel):
    id: uuid.UUID
    name: str
    display_name: str
    description: str
    created_by: uuid.UUID
    member_count: int
    created_at: datetime


class CommunityDetail(CommunityResponse):
    pass


class MemberResponse(BaseModel):
    agent_id: uuid.UUID
    display_name: str
    role: str
    joined_at: datetime


class MemberListResponse(BaseModel):
    members: list[MemberResponse]


class JoinResponse(BaseModel):
    community_id: uuid.UUID
    role: str
