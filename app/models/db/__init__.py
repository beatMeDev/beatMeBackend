"""Explore models for tortoise orm"""
from .challenge import Challenge
from .playlist import Playlist
from .track import Track
from .user import AuthAccount
from .user import User


__models__ = [
    User,
    AuthAccount,
    Playlist,
    Track,
    Challenge,
]
