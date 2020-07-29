"""Explore models for tortoise orm"""
from .user import AuthAccount
from .user import User
from .playlist import Playlist
from .track import Track
from .challenge import Challenge


__models__ = [
    User,
    AuthAccount,
    Playlist,
    Track,
    Challenge,
]
