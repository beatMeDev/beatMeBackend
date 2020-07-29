"""User models"""
from enum import Enum
from typing import Iterator
from typing import List

from tortoise import fields
from tortoise import models


class AuthProvider(str, Enum):
    """Auth providers enum."""
    DEFAULT = "DEFAULT"
    SPOTIFY = "SPOTIFY"
    GOOGLE = "GOOGLE"
    VK = "VK"
    FACEBOOK = "FACEBOOK"

    def __iter__(self) -> Iterator[str]:
        return iter([self.SPOTIFY, self.GOOGLE, self.VK, self.FACEBOOK])


class User(models.Model):
    """User model."""
    id = fields.UUIDField(pk=True)
    auth_accounts = fields.ManyToManyField(
        "models.AuthAccount", related_name="users", through="users_auth_accounts"
    )

    def name(self) -> str:
        """Last auth account name."""
        return getattr(self.auth_accounts[-1], "name")  # pylint: disable=unsubscriptable-object

    def image(self) -> str:
        """Last auth account image."""
        return getattr(self.auth_accounts[-1], "image")  # pylint: disable=unsubscriptable-object

    def url(self) -> str:
        """Last auth account image."""
        return getattr(self.auth_accounts[-1], "url")  # pylint: disable=unsubscriptable-object

    def providers(self) -> List[str]:
        """User's auth accounts provides."""
        return [getattr(auth_account, "provider") for auth_account in self.auth_accounts]  # pylint: disable=not-an-iterable

    class PydanticMeta:  # pylint: disable=too-few-public-methods
        """Serializations options."""
        exclude = ("own_challenges", "challenges", )
        computed = ("name", "image", "url", "providers", )


class AuthAccount(models.Model):
    """Auth account model."""
    _id = fields.UUIDField(pk=True)
    id = fields.CharField(max_length=255, null=False)
    name = fields.CharField(max_length=255, null=True)
    image = fields.CharField(max_length=2048, null=True)
    url = fields.CharField(max_length=2048, null=True)
    provider = fields.CharEnumField(AuthProvider, default=None)

    access_token = fields.CharField(max_length=1024, null=True)
    refresh_token = fields.CharField(max_length=1024, null=True)
    expires = fields.IntField(null=True)

    class PydanticMeta:  # pylint: disable=too-few-public-methods
        """Serializations options."""
        exclude = ("access_token", "refresh_token", "expires",)
