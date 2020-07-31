"""Submission models."""
from tortoise import fields, Tortoise

from app.models.db.base import BaseModel


class Submission(BaseModel):
    """Submission models."""

    url = fields.CharField(max_length=1024, null=False)

    challenge = fields.ForeignKeyField("models.Challenge", related_name="submissions")
    user = fields.ForeignKeyField("models.User", related_name="submissions")

    class PydanticMeta:  # pylint: disable=too-few-public-methods
        """Serializations options."""

        exclude_raw_fields = True


Tortoise.init_models(
    ["app.models.db.submission", "app.models.db.user", "app.models.db.challenge", ], "models"
)  # pydantic schema hack
