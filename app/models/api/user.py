"""User pydantic schemas"""
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.db.user import User


UserOut = pydantic_model_creator(User, name="User")
UserIn = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
