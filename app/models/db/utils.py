"""Utils models."""
from tortoise import fields

from app.models.db.base import BaseModel


class Text(BaseModel):
    """Text for loaders."""

    content = fields.TextField()
