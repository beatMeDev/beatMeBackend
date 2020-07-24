from enum import Enum
from typing import Iterator

from tortoise import Tortoise
from tortoise import fields
from tortoise import models


class AuthProvider(str, Enum):
    DEFAULT = "DEFAULT"
    SPOTIFY = "SPOTIFY"
    GOOGLE = "GOOGLE"
    VK = "VK"
    FACEBOOK = "FACEBOOK"

    def __iter__(self) -> Iterator[str]:
        return iter([self.SPOTIFY, self.GOOGLE, self.VK, self.FACEBOOK])


class User(models.Model):
    id = fields.UUIDField(pk=True)
    auth_accounts = fields.ManyToManyField(
        "models.AuthAccount", related_name="users", through="users_auth_accounts"
    )

    class PydanticMeta:
        pass


class AuthAccount(models.Model):
    _id = fields.UUIDField(pk=True)
    id = fields.CharField(max_length=255, null=False)
    access_token = fields.CharField(max_length=1024, null=True)
    name = fields.CharField(max_length=255, null=True)
    image = fields.CharField(max_length=2048, null=True)
    url = fields.CharField(max_length=2048, null=True)
    provider = fields.CharEnumField(AuthProvider, default=None)

    class PydanticMeta:
        exclude = ("access_token",)


Tortoise.init_models(["app.models.db.user"], "models")  # pydantic schema hack
