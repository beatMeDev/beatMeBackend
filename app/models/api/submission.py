# pylint: skip-file
"""Submission pydantic schemas"""
import re

from typing import List

from pydantic import validator
from pydantic.main import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.pydantic import pydantic_queryset_creator

from app.models.db import Submission


SOUNDCLOUD_REGEX = re.compile(r"https://soundcloud.com/[a-zA-Z-0-9]*/[A-Za-z-0-9]*")

SubmissionOut = pydantic_model_creator(Submission, name="Submission")
SubmissionList = pydantic_queryset_creator(Submission, name="SubmissionList")


class SubmissionListOut(BaseModel):
    count: int
    items: List[SubmissionOut]  # type: ignore


class SubmissionIn(BaseModel):
    url: str

    @validator("url")
    def url_is_soundcloud(cls, value: str) -> str:
        if SOUNDCLOUD_REGEX.findall(value):
            return value

        raise ValueError("Must to be soundcloud URL")
