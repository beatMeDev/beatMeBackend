"""Playlist services"""
from typing import Optional

from fastapi import Depends
from tortoise.contrib.pydantic import PydanticModel

from app.models.api.playlist import PlaylistIn
from app.models.api.playlist import PlaylistOut
from app.models.db.playlist import Playlist
from app.services.auth.providers.spotify import spotify_auth
from app.services.spotify import get_playlist_id
from app.services.spotify import get_playlist_info
from app.services.tracks import add_tracks_to_playlist
from app.utils.exceptions import BadRequestError


async def create_playlist(link: str, access_token: str) -> Playlist:
    """
    Create playlist by spotify link
    :param link: spotify url/uri
    :param access_token: spotify user's token
    :return: playlist
    """
    playlist_id: Optional[str] = await get_playlist_id(link)

    if not playlist_id:
        raise BadRequestError

    playlist_info, tracks = await get_playlist_info(
        playlist_id=playlist_id, access_token=access_token
    )
    playlist, _ = await Playlist.get_or_create(**playlist_info)  # type: ignore
    await add_tracks_to_playlist(playlist=playlist, tracks=tracks)

    return playlist


async def create_playlist_controller(
        playlist_data: PlaylistIn, access_token: str = Depends(spotify_auth),
) -> PydanticModel:
    """Controller for using as dependency."""
    playlist: Playlist = await create_playlist(link=playlist_data.link, access_token=access_token)
    response: PydanticModel = await PlaylistOut.from_tortoise_orm(playlist)

    return response
