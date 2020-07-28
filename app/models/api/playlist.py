# pylint: skip-file
"""Playlist pydantic schemas"""
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.db import Playlist

PlaylistOut = pydantic_model_creator(Playlist, name="Playlist")


class PlaylistIn(BaseModel):
    link: str
