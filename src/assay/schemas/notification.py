import uuid
from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    type: str
    source_agent_id: uuid.UUID | None
    target_type: str
    target_id: uuid.UUID
    preview: str | None
    is_read: bool
    created_at: datetime
