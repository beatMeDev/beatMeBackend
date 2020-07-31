"""Playlist models"""
from tortoise import fields

from app.models.db.base import BaseModel


class Playlist(BaseModel):
    """Playlist model."""

    name = fields.CharField(max_length=255, null=True)
    url = fields.CharField(max_length=255, null=True)
    spotify_id = fields.CharField(max_length=255, null=True)
    recommended = fields.BooleanField(null=True, default=True)

    tracks = fields.ManyToManyField(
        "models.Track", related_name="playlists", through="playlists_tracks"
    )

    def __str__(self) -> str:
        return str(self.name)

    class PydanticMeta:  # pylint: disable=too-few-public-methods
        """Serializations options."""

        exclude = ("tracks",)
