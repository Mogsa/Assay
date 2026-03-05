from typing import Literal

from pydantic import BaseModel


class VoteCreate(BaseModel):
    value: Literal[-1, 1]


class VoteActionResponse(BaseModel):
    status: Literal["created", "removed", "changed"]
    viewer_vote: Literal[-1, 1] | None
    upvotes: int
    downvotes: int
    score: int
