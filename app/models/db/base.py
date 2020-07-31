"""Base db stuff."""
from tortoise import fields
from tortoise import models


class BaseModel(models.Model):
    """Default tortoise model."""

    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
