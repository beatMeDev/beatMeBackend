"""Track models"""
from tortoise import fields, Tortoise
from tortoise import models


class Track(models.Model):
    """
    meta example:
        {
            "album": "album name",
            "key": "D♭ Major",
            "camelot": "3B",
            "bpm": "102",
            "duration": 205
        }
    """
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255, null=True)
    author_name = fields.CharField(max_length=255, null=True)
    cover_url = fields.CharField(max_length=255, null=True)
    preview_url = fields.CharField(max_length=255, null=True)
    youtube_id = fields.CharField(max_length=255, null=True)
    spotify_id = fields.CharField(max_length=255, null=True)

    recommended = fields.BooleanField(null=True, default=False)
    meta = fields.JSONField()


Tortoise.init_models(["app.models.db.track"], "models")  # pydantic schema hack