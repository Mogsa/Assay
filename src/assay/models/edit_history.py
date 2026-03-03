import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class EditHistory(Base):
    __tablename__ = "edit_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    target_type: Mapped[str] = mapped_column(String(16))  # "question" or "answer"
    target_id: Mapped[uuid.UUID] = mapped_column()
    editor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    field_name: Mapped[str] = mapped_column(String(32))  # "title", "body", or "status"
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
