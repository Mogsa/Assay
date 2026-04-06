import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from assay.models.activity_log import ActivityLog


async def create_activity_entry(
    db: AsyncSession,
    actor_id: uuid.UUID,
    action: str,
    target_type: str,
    target_id: uuid.UUID,
    summary: str,
) -> None:
    """Append an entry to the activity log. Caller handles commit."""
    entry = ActivityLog(
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        summary=summary[:200],
    )
    db.add(entry)
