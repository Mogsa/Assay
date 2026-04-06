import uuid
from datetime import datetime

from pydantic import BaseModel


class QuestionUpdate(BaseModel):
    title: str | None = None
    body: str | None = None


class AnswerUpdate(BaseModel):
    body: str | None = None


class EditHistoryEntry(BaseModel):
    id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    editor_id: uuid.UUID
    field_name: str
    old_value: str | None
    new_value: str
    created_at: datetime
