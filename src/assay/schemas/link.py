import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class LinkCreate(BaseModel):
    source_type: Literal["question", "answer"]
    source_id: uuid.UUID
    target_type: Literal["question", "answer"]
    target_id: uuid.UUID
    link_type: Literal["references", "extends", "contradicts", "solves"]


class LinkResponse(BaseModel):
    id: uuid.UUID
    source_type: str
    source_id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    link_type: str
    created_by: uuid.UUID
    created_at: datetime
