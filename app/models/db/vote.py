"""Vote models."""
from tortoise import Tortoise
from tortoise import fields

from app.models.db.base import BaseModel


class Vote(BaseModel):
    """Voting model."""

    user = fields.ForeignKeyField("models.User", related_name="votes")
    submission = fields.ForeignKeyField("models.Submission", related_name="votes")

    class PydanticMeta:  # pylint: disable=too-few-public-methods
        """Serializations options."""

        exclude = ("user",)
        exclude_raw_fields = True


Tortoise.init_models(
    ["app.models.db.vote", "app.models.db.user", "app.models.db.submission", ], "models"
)  # pydantic schema hack
