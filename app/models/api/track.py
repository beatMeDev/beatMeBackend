# pylint: skip-file
"""Track pydantic schemas"""
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.db import Track

TrackOut = pydantic_model_creator(Track, name="Track")
