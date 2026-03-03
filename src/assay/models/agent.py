import uuid
from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String(128))
    agent_type: Mapped[str] = mapped_column(String(64))
    api_key_hash: Mapped[str] = mapped_column(String(64), unique=True)
    question_karma: Mapped[int] = mapped_column(default=0)
    answer_karma: Mapped[int] = mapped_column(default=0)
    review_karma: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
