"""Explore models for tortoise orm"""
from .db.user import AuthAccount
from .db.user import User


__models__ = [
    AuthAccount,
    User,
]
