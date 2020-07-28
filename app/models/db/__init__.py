"""Explore models for tortoise orm"""
from .user import AuthAccount
from .user import User
from .playlist import Playlist
from .track import Track


__models__ = [
    AuthAccount,
    User,
    Playlist,
    Track,
]
