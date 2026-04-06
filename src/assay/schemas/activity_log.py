import uuid
from datetime import datetime

from pydantic import BaseModel


class ActivityLogEntry(BaseModel):
    id: uuid.UUID
    actor_id: uuid.UUID
    actor_name: str
    action: str
    target_type: str
    target_id: uuid.UUID
    summary: str
    created_at: datetime
