# pylint: skip-file
"""Text pydantic schemas"""
from typing import List

from pydantic.main import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.pydantic import pydantic_queryset_creator

from app.models.db import Text


TextOut = pydantic_model_creator(Text, name="Text")
TextList = pydantic_queryset_creator(Text, name="TextList")


class TextListOut(BaseModel):
    count: int
    items: List[TextOut]  # type: ignore
