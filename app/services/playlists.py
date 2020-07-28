"""Playlist services"""
from typing import Optional

from app.models.db.playlist import Playlist
from app.services.spotify import get_playlist_id, get_playlist_info
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
    playlist, _ = await Playlist.get_or_create(playlist_info)
    await add_tracks_to_playlist(playlist=playlist, tracks=tracks)

    return playlist
