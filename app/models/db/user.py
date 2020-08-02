"""User models"""
from enum import Enum
from typing import List

from tortoise import fields

from app.models.db.base import BaseModel


class AuthProvider(str, Enum):
    """Auth providers enum."""

    DEFAULT = "DEFAULT"
    SPOTIFY = "SPOTIFY"
    GOOGLE = "GOOGLE"
    VK = "VK"
    FACEBOOK = "FACEBOOK"


class User(BaseModel):
    """User model."""

    auth_accounts = fields.ManyToManyField(
        "models.AuthAccount", related_name="users", through="users_auth_accounts",
    )

    def name(self) -> str:
        """Last auth account name."""
        return getattr(
            self.auth_accounts[-1], "name"  # pylint: disable=unsubscriptable-object
        )

    def image(self) -> str:
        """Last auth account image."""
        return getattr(
            self.auth_accounts[-1], "image"  # pylint: disable=unsubscriptable-object
        )

    def url(self) -> str:
        """Last auth account image."""
        return getattr(
            self.auth_accounts[-1], "url"  # pylint: disable=unsubscriptable-object
        )

    def providers(self) -> List[str]:
        """User's auth accounts provides."""
        return [
            getattr(auth_account, "provider")
            for auth_account in self.auth_accounts  # pylint: disable=not-an-iterable
        ]

    def __str__(self) -> str:
        return self.name()

    class PydanticMeta:  # pylint: disable=too-few-public-methods
        """Serializations options."""

        exclude = (
            "own_challenges",
            "challenges",
            "submissions",
            "votes",
        )
        computed = (
            "name",
            "image",
            "url",
            "providers",
        )


class AuthAccount(BaseModel):
    """Auth account model."""

    _id = fields.CharField(max_length=255, null=False)
    name = fields.CharField(max_length=255, null=True)
    image = fields.CharField(max_length=2048, null=True)
    url = fields.CharField(max_length=2048, null=True)
    provider = fields.CharEnumField(AuthProvider, default=None)

    access_token = fields.CharField(max_length=1024, null=True)
    refresh_token = fields.CharField(max_length=1024, null=True)
    expires = fields.IntField(null=True)

    class PydanticMeta:  # pylint: disable=too-few-public-methods
        """Serializations options."""

        exclude = (
            "access_token",
            "refresh_token",
            "expires",
        )
