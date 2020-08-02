"""Playlist endpoints"""
from fastapi import APIRouter
from fastapi import Depends
from tortoise.contrib.pydantic import PydanticModel

from app.models.api.playlist import PlaylistOut
from app.services.playlists import create_playlist_controller


playlists_router = APIRouter()  # pylint: disable-msg=C0103


@playlists_router.post("/", response_model=PlaylistOut)
async def create_playlist_route(
        response: PydanticModel = Depends(create_playlist_controller),
) -> PydanticModel:
    """
    Create spotify playlist.
    :param response: response instance
    :return: response
    """
    return response
