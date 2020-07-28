"""Playlist endpoints"""
from fastapi import APIRouter, Depends
from tortoise.contrib.pydantic import PydanticModel

from app.models.api.playlist import PlaylistOut, PlaylistIn
from app.models.db import Playlist
from app.services.auth.providers.spotify import spotify_auth
from app.services.playlists import create_playlist

playlists_router = APIRouter()  # pylint: disable-msg=C0103


@playlists_router.post("/", response_model=PlaylistOut)
async def create_playlist_route(
        playlist_data: PlaylistIn,
        access_token: str = Depends(spotify_auth)
) -> PydanticModel:
    """
    Create spotify playlist.
    :param playlist_data: data with spotify url/uri
    :param access_token: spotify user's token
    :return: response
    """
    playlist: Playlist = await create_playlist(link=playlist_data.link, access_token=access_token)
    response: PydanticModel = await PlaylistOut.from_tortoise_orm(playlist)

    return response
