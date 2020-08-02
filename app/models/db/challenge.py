"""Challenge models"""
from typing import Dict
from typing import Optional

import jwt

from tortoise import Tortoise
from tortoise import fields

from app.models.db.base import BaseModel
from app.settings import ITEM_SECRET
from app.settings import JWT_ALGORITHM
from app.utils.exceptions import PermissionsDeniedError


class Challenge(BaseModel):
    """Challenge model."""

    name = fields.CharField(max_length=255, null=True)
    challenge_end = fields.DatetimeField(null=False)
    vote_end = fields.DatetimeField(null=False)
    is_public = fields.BooleanField(null=True, default=True)
    is_open = fields.BooleanField(null=True, default=True)
    owner = fields.ForeignKeyField("models.User", related_name="own_challenges")
    track = fields.ForeignKeyField("models.Track", related_name="challenges")

    participants = fields.ManyToManyField(
        "models.User", related_name="challenges", through="challenges_participants"
    )

    def secret_key(self) -> Optional[str]:
        """
        Create item access secret key, it is jwt with item id inside.
        :return: secret string
        """
        if self.is_public is True:
            return None

        payload: Dict[str, str] = {"id": str(self.id)}
        secret: str = jwt.encode(
            payload=payload, key=ITEM_SECRET, algorithm=JWT_ALGORITHM,
        ).decode("utf-8")

        return secret

    def check_secret(self, secret: Optional[str]) -> bool:
        """
        Check secret key.
        :param secret: secret string
        :return: true if everything is good
        """
        if not secret or secret != self.secret_key():
            raise PermissionsDeniedError

        return True

    class PydanticMeta:  # pylint: disable=too-few-public-methods
        """Serializations options."""

        exclude = ("participants", "submissions", "votes", )
        computed = ("secret_key", )
        exclude_raw_fields = True


Tortoise.init_models(
    ["app.models.db.challenge", "app.models.db.user", "app.models.db.track", ], "models"
)  # pydantic schema hack
