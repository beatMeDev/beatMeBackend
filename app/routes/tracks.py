"""Tracks endpoints"""
from random import randint
from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from tortoise.contrib.pydantic import PydanticModel

from app.models.api.track import TrackOut
from app.models.db import Track


tracks_router = APIRouter()  # pylint: disable-msg=C0103


@tracks_router.get("/random/", response_model=TrackOut, summary="Return random track")
async def get_random_track_route() -> PydanticModel:
    """
    Get random recommended track.
    :return: track
    """
    count: int = await Track.filter(recommended=True).count()
    offset: int = randint(0, count - 1)
    track: Optional[Track] = await Track.filter(recommended=True).limit(1).offset(
        offset
    ).first()
    response: PydanticModel = await TrackOut.from_tortoise_orm(track)

    return response


@tracks_router.get("/{track_id}/", response_model=TrackOut, summary="Return track")
async def get_track_route(track_id: UUID) -> PydanticModel:
    """
    Get track by id.
    :param track_id: track id
    :return: track
    """
    track: Track = await Track.get(id=track_id)
    response: PydanticModel = await TrackOut.from_tortoise_orm(track)

    return response
