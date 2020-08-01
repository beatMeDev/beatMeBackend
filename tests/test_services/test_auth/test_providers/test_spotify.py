"""Tests for Spotify auth provider."""
from typing import Any
from typing import Dict
from unittest import mock
from unittest.mock import MagicMock

import pytest

from freezegun import freeze_time  # type: ignore
from truth.truth import AssertThat  # type: ignore

from app.services.auth.providers.spotify import refresh_spotify_token
from app.utils.exceptions import UnauthorizedError
from tests.test_services.base import get_response_mock


@pytest.mark.asyncio
@freeze_time("1970-01-01")
@mock.patch("app.extensions.http_client.post")
async def test_refresh_spotify_token_valid_response(
        response_post_mock: MagicMock,
) -> None:
    """Check refresh_spotify_token if response is valid."""
    refresh_token: str = "test_refresh"
    response_data: Dict[str, Any] = {
        "access_token": "test_token",
        "expires_in": 1,
    }
    response_post_mock.return_value = get_response_mock(
        method="POST", response_data=response_data, valid=True,
    )

    access_token, new_refresh_token, expires = await refresh_spotify_token(
        refresh_token=refresh_token
    )

    AssertThat(access_token).IsEqualTo(response_data["access_token"])
    AssertThat(new_refresh_token).IsEqualTo(refresh_token)
    AssertThat(expires).IsEqualTo(response_data["expires_in"])


@pytest.mark.asyncio
@mock.patch("app.extensions.http_client.post")
async def test_refresh_spotify_token_invalid_response(
        response_post_mock: MagicMock,
) -> None:
    """Check refresh_spotify_token if response is not valid."""
    response_data: Dict[str, Any] = {}
    response_post_mock.return_value = get_response_mock(
        method="GET", response_data=response_data, valid=False,
    )

    with AssertThat(UnauthorizedError).IsRaised():
        await refresh_spotify_token(refresh_token="test")
