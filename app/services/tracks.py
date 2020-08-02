"""Track services"""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from app.models.db.playlist import Playlist
from app.models.db.track import Track


def format_track(track_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Format raw track data to database model fields.
    :param track_info: raw track data
    :return: formatted track data
    """
    raw_track_data: Dict[str, Any] = track_info.get("track", {})
    raw_album_data: Dict[str, Any] = raw_track_data.get("album", {})

    if not raw_track_data:
        return None

    track_id: Optional[str] = raw_track_data.get("id")

    if not track_id:
        return None

    author_name: str = ", ".join(
        [artist["name"] for artist in raw_track_data.get("artists", [])]
    )
    track_name: Optional[str] = raw_track_data.get("name")
    cover_images: List[Dict[str, Any]] = raw_album_data.get("images", [])
    cover_image: Optional[str] = ""

    if cover_images:
        cover_image = cover_images[0].get("url")

    meta: Dict[str, Any] = {
        "album": raw_album_data.get("name"),
        "duration": raw_track_data.get("duration_ms", 0) / 1000,
    }

    track_data: Dict[str, Any] = {
        "name": track_name,
        "author_name": author_name,
        "cover_url": cover_image,
        "preview_url": raw_track_data.get("preview_url"),
        "spotify_id": raw_track_data.get("id"),
        "recommended": True,
        "meta": meta,
    }

    return track_data


async def add_tracks_to_playlist(
        playlist: Playlist, tracks: List[Dict[str, Any]]
) -> bool:
    """
    Add formatted tracks to playlist.
    :param playlist: Playlist object
    :param tracks: raw tracks list
    :return: nothing
    """
    for track_info in tracks:
        formatted_track: Optional[Dict[str, Any]] = format_track(track_info)

        if not formatted_track:
            continue

        track, _ = await Track.get_or_create(**formatted_track)
        await playlist.tracks.add(track)

    return True
