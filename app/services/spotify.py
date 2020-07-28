"""Spotify services"""
import re
from typing import Dict, List, Any, Tuple, Optional

from httpx import Response, HTTPError

from app.extensions import http_client
from app.settings import SPOTIFY_API
from app.utils.exceptions import UnauthorizedError, NotFoundError

playlist_id_regex = re.compile(r"playlist.\w+")
playlist_regex = re.compile(r"playlist.")


async def get_playlist_id(string: str) -> Optional[str]:
    """
    Extract playlist id from playlist url or spotify uri.
    :param string: playlist url or spotify uri
    :return: playlist id if matched
    """
    match: Optional[re.Match[str]] = playlist_id_regex.search(string)

    if not match:
        return None

    result: str = playlist_regex.split(match.group())[-1]

    return result


async def get_playlist_info(
        playlist_id: str, access_token: str
) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
    """
    Get playlist tracks.
    :param playlist_id: playlist spotify's id
    :param access_token: spotify user token
    :return: playlist info and list with tracks data
    """
    resource = "playlists"
    url = f"{SPOTIFY_API}{resource}/{playlist_id}"
    headers: Dict[str, str] = {
        "Authorization": f"Bearer {access_token}"
    }
    response: Response = await http_client.get(url=url, headers=headers)

    try:
        response.raise_for_status()
    except HTTPError as exception:
        if exception.response and exception.response.status_code == 404:
            raise NotFoundError

        raise UnauthorizedError

    response_data = response.json()

    tracks: List[Dict[str, Any]] = response_data.get("tracks", {}).get("items", [])
    playlist_info: Dict[str, str] = {
        "url": url,
        "name": response_data.get("name"),
        "spotify_id": playlist_id,
    }

    return playlist_info, tracks
