# pylint: skip-file
"""Vote pydantic schemas"""

from typing import List
from uuid import UUID

from pydantic.main import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.pydantic import pydantic_queryset_creator

from app.models.db import Vote

VoteOut = pydantic_model_creator(Vote, name="Vote")
VoteList = pydantic_queryset_creator(Vote, name="VoteList")


class VoteListOut(BaseModel):
    count: int
    items: List[VoteOut]  # type: ignore


class VoteIn(BaseModel):
    submission_id: UUID


class VoteCount(BaseModel):
    count: int
