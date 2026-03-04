import uuid
from collections.abc import Mapping

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.models.answer import Answer
from assay.models.comment import Comment
from assay.models.question import Question

TARGET_MODELS: Mapping[str, type[Question | Answer | Comment]] = {
    "question": Question,
    "answer": Answer,
    "comment": Comment,
}


async def get_target_or_404(
    db: AsyncSession,
    target_type: str,
    target_id: uuid.UUID,
    allowed_types: Mapping[str, type[Question | Answer | Comment]] | None = None,
) -> Question | Answer | Comment:
    models = allowed_types or TARGET_MODELS
    model = models.get(target_type)
    if model is None:
        raise HTTPException(status_code=400, detail="Unsupported target type")

    result = await db.execute(select(model).where(model.id == target_id))
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail=f"{target_type.title()} not found")
    return target
