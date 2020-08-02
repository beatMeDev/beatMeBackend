"""Vote models."""
from tortoise import fields

from app.models.db.base import BaseModel


class Vote(BaseModel):
    """Voting model."""

    user = fields.ForeignKeyField("models.User", related_name="votes")
    submission = fields.ForeignKeyField("models.Submission", related_name="votes")

    class PydanticMeta:  # pylint: disable=too-few-public-methods
        """Serializations options."""

        exclude = ("user", "submission", )
        exclude_raw_fields = True
