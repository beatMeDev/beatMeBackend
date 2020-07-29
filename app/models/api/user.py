# pylint: skip-file
"""User pydantic schemas"""
from typing import List

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.pydantic import pydantic_queryset_creator

from app.models.db.user import User


UserOut = pydantic_model_creator(User, name="User")
UserIn = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

UserList = pydantic_queryset_creator(User, name="UserList")


class UserListOut(BaseModel):
    count: int
    items: List[UserOut]  # type: ignore
