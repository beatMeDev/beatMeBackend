"""Spotify services tests."""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from unittest import mock
from unittest.mock import MagicMock

import pytest

from truth.truth import AssertThat  # type: ignore

from app.services.spotify import get_playlist_id
from app.services.spotify import get_playlist_info
from app.utils.exceptions import NotFoundError
from app.utils.exceptions import UnauthorizedError
from tests.test_services.base import get_response_mock


fixtures: List[Tuple[str, Optional[str]]] = [
    (
        "https://open.spotify.com/playlist/37i9dQZF1DZ06evO0Co11u?si=vnGAgLvERLCkdDhmO0aIBQ",
        "37i9dQZF1DZ06evO0Co11u",
    ),
    ("https://open.spotify.com/playlist/37i9dQZF1DZ06evO0Co11u", "37i9dQZF1DZ06evO0Co11u",),
    ("spotify:playlist:37i9dQZF1DZ06evO0Co11u", "37i9dQZF1DZ06evO0Co11u",),
    ("trash:123test321", None,),
    ("https://open.spotify.com/track/1qCQTy0fTXerET4x8VHyr9?si=mfixiwJLQ0i4_zV_8Pik7w", None,),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "link,expected_result", fixtures
)
async def test_get_playlist_id(link: str, expected_result: Optional[str]) -> None:
    """Test playlist_id was correctly extracted from links."""
    playlist_id: Optional[str] = await get_playlist_id(string=link)

    AssertThat(playlist_id).IsEqualTo(expected_result)


@pytest.mark.asyncio
@mock.patch("app.extensions.http_client.get")
async def test_get_playlist_info_not_found(
        response_get_mock: MagicMock,
) -> None:
    """Test get playlist info if playlist was not found."""
    response_get_mock.return_value = get_response_mock(
        method="POST", response_data={}, valid=False, status=404,
    )

    with AssertThat(NotFoundError).IsRaised():
        await get_playlist_info(playlist_id="test", access_token="test")


@pytest.mark.asyncio
@mock.patch("app.extensions.http_client.get")
async def test_get_playlist_info_bad_request(
        response_get_mock: MagicMock,
) -> None:
    """Test get playlist info if bad request."""
    response_get_mock.return_value = get_response_mock(
        method="POST", response_data={}, valid=False,
    )

    with AssertThat(UnauthorizedError).IsRaised():
        await get_playlist_info(playlist_id="test", access_token="test")


@pytest.mark.asyncio
@mock.patch("app.extensions.http_client.get")
async def test_get_playlist_info(
        response_get_mock: MagicMock,
) -> None:
    """Test get playlist info if everything is fine."""
    playlist_id: str = "test"
    expected_tracks: List[Dict[str, Any]] = [{"name": "test"}]
    expected_playlist: Dict[str, Any] = {
        "url": "test_url",
        "name": "test",
        "spotify_id": playlist_id,
    }
    response_data: Dict[str, Any] = {
        "external_urls": {"spotify": expected_playlist["url"]},
        "name": expected_playlist["name"],
        "tracks": {"items": expected_tracks},
    }
    response_get_mock.return_value = get_response_mock(
        method="POST", response_data=response_data, valid=True,
    )

    playlist_info, tracks = await get_playlist_info(
        playlist_id=playlist_id, access_token="test"
    )

    AssertThat(playlist_info).IsEqualTo(expected_playlist)
    AssertThat(tracks).IsEqualTo(expected_tracks)
