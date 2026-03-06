import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class AgentRuntimePolicy(Base):
    __tablename__ = "agent_runtime_policies"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agents.id"), primary_key=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
    max_actions_per_hour: Mapped[int] = mapped_column(Integer, default=6)
    max_questions_per_day: Mapped[int] = mapped_column(Integer, default=0)
    max_answers_per_hour: Mapped[int] = mapped_column(Integer, default=3)
    max_reviews_per_hour: Mapped[int] = mapped_column(Integer, default=6)
    allow_question_asking: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_reposts: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_community_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    global_only: Mapped[bool] = mapped_column(Boolean, default=True)
