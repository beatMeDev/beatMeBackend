"""
Auth pydantic models
"""
from pydantic import BaseModel


class AuthIn(BaseModel):
    code: str


class AuthOut(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: int


class LogoutOut(BaseModel):
    data: bool
