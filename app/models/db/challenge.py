"""Challenge models"""
from datetime import datetime, timedelta
from typing import Optional, Dict

import jwt
from tortoise import fields, Tortoise
from tortoise import models

from app.settings import JWT_ALGORITHM, ITEM_SECRET
from app.utils.exceptions import PermissionsDeniedError


def challenge_end_date(days: int = 1) -> datetime:
    """
    Default challenge end date
    :param days: how much days challenge will be open
    :return: end date
    """
    now_time = datetime.utcnow()
    end_date = now_time + timedelta(days=days)

    return end_date


def vote_end_date(days: int = 2) -> datetime:
    """
    Default voting end date
    :param days: how much days voting will be open
    :return: end date
    """
    now_time = datetime.utcnow()
    end_date = now_time + timedelta(days=days)

    return end_date


class Challenge(models.Model):
    """Challenge model."""
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255, null=True)
    challenge_end = fields.DatetimeField(null=True, default=challenge_end_date)
    vote_end = fields.DatetimeField(null=True, default=vote_end_date)
    is_public = fields.BooleanField(null=True, default=True)
    is_open = fields.BooleanField(null=True, default=True)
    owner = fields.ForeignKeyField('models.User', related_name='own_challenges')
    track = fields.ForeignKeyField('models.Track', related_name='challenges')

    created_at = fields.DatetimeField(null=True, auto_now=True)

    participants = fields.ManyToManyField(
        "models.User", related_name="challenges", through="participants_users"
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
            payload=payload,
            key=ITEM_SECRET,
            algorithm=JWT_ALGORITHM,
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
        exclude = ("participants", )
        computed = ("secret_key", )
        exclude_raw_fields = True


Tortoise.init_models([
    "app.models.db.user",
    "app.models.db.track",
    "app.models.db.challenge",
], "models")  # pydantic schema hack
