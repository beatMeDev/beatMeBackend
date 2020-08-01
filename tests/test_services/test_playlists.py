"""Test playlists services."""
from typing import Dict
from unittest import mock
from unittest.mock import MagicMock

import pytest

from truth.truth import AssertThat  # type: ignore

from app.models.db import Playlist
from app.services.playlists import create_playlist
from app.utils.exceptions import BadRequestError


@pytest.mark.asyncio
async def test_create_playlist_link_is_not_valid() -> None:
    """Check create playlist if link is not valid."""
    with AssertThat(BadRequestError).IsRaised():
        await create_playlist(link="trash", access_token="test")


@pytest.mark.asyncio
@mock.patch("app.services.playlists.get_playlist_info")
async def test_create_playlist_link(
        get_playlist_info_mock: MagicMock,
) -> None:
    """Check create playlist if everything is fine."""
    playlist_id: str = "37i9dQZF1DZ06evO0Co11u"
    link: str = f"https://open.spotify.com/playlist/{playlist_id}"
    playlist_info: Dict[str, str] = {
        "url": "test_url",
        "name": "test",
        "spotify_id": playlist_id,
    }
    get_playlist_info_mock.return_value = (playlist_info, [])

    playlist: Playlist = await create_playlist(link=link, access_token="test")

    AssertThat(playlist.spotify_id).IsEqualTo(playlist_id)
    AssertThat(playlist.url).IsEqualTo(playlist_info["url"])
    AssertThat(playlist.name).IsEqualTo(playlist_info["name"])
