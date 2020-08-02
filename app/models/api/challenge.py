# pylint: skip-file
"""Challenge pydantic schemas"""
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import validator
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.pydantic import pydantic_queryset_creator

from app.models.db.challenge import Challenge


ChallengeOut = pydantic_model_creator(Challenge, name="Challenge")
ChallengeList = pydantic_queryset_creator(Challenge, name="ChallengeList")


class ChallengeListOut(BaseModel):
    count: int
    items: List[ChallengeOut]  # type: ignore


class ChallengeIn(BaseModel):
    name: str
    challenge_end: datetime
    vote_end: datetime
    is_public: bool = True
    is_open: bool = True
    track_id: UUID

    @validator("vote_end")
    def vote_end_validator(
        cls, value: datetime, values: Dict[str, Any]
    ) -> datetime:
        """Validate vote end date."""
        if value.replace(tzinfo=None) < datetime.utcnow():
            raise ValueError("must be greater than `now`")

        challenge_end: Optional[datetime] = values.get("challenge_end")

        if not challenge_end:
            return value

        if value > challenge_end:
            return value

        raise ValueError("must be greater than `challenge_end`")

    @validator("challenge_end")
    def challenge_end_validator(cls, value: datetime) -> datetime:
        """Validate challenge end date."""
        now = datetime.utcnow()

        if now <= value.replace(tzinfo=None):
            return value

        raise ValueError("must be greater than `now`")

    @validator("name")
    def name_exists(cls, value: str) -> str:
        """Validate name."""
        if value:
            return value

        raise ValueError("must not be empty")
