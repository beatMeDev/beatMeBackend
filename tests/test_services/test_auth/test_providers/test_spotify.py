"""Tests for Spotify auth provider."""
from typing import Any
from typing import Dict
from unittest import mock
from unittest.mock import MagicMock

import pytest

from freezegun import freeze_time  # type: ignore
from truth.truth import AssertThat  # type: ignore

from app.models.db import AuthAccount
from app.models.db import User
from app.models.db.user import AuthProvider
from app.services.auth.providers.spotify import refresh_spotify_token
from app.services.auth.providers.spotify import spotify_auth
from app.utils.exceptions import UnauthorizedError
from tests.test_services.base import get_response_mock
from tests.test_services.test_auth.test_base import USER_UUID


auth_account_data: Dict[str, Any] = {
    "_id": "test",
    "name": "test",
    "image": "test",
    "url": "test",
    "provider": AuthProvider.SPOTIFY,
    "access_token": "test",
    "refresh_token": "test",
    "expires": 1,
}


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


@pytest.mark.asyncio
async def test_spotify_auth_empty_user() -> None:
    """Test spotify auth if user_id is None."""
    with AssertThat(UnauthorizedError).IsRaised():
        await spotify_auth(user_id=None)


@pytest.mark.asyncio
async def test_spotify_auth_empty_auth_account() -> None:
    """Test spotify auth if user has no auth account."""
    user: User = await User.create(id=USER_UUID)

    with AssertThat(UnauthorizedError).IsRaised():
        await spotify_auth(user_id=str(user.id))


@pytest.mark.asyncio
@freeze_time("1970-01-01")
async def test_spotify_auth_token_is_alive() -> None:
    """Test spotify auth if spotify access token is alive."""
    user: User = await User.create(id=USER_UUID)
    auth_account: AuthAccount = await AuthAccount.create(**auth_account_data)
    await user.auth_accounts.add(auth_account)

    access_token: str = await spotify_auth(user_id=str(user.id))

    AssertThat(access_token).IsEqualTo(auth_account_data["access_token"])


@pytest.mark.asyncio
@freeze_time("1970-01-01")
@mock.patch("app.services.auth.providers.spotify.refresh_spotify_token")
async def test_spotify_auth_token_is_not_alive(
        refresh_spotify_token_mock: MagicMock
) -> None:
    """Test spotify auth if spotify access token is not alive."""
    new_access_token: str = "new_test_token"
    refresh_spotify_token_mock.return_value = (new_access_token, "test", 2)
    auth_account_data["expires"] = -1
    user: User = await User.create(id=USER_UUID)
    auth_account: AuthAccount = await AuthAccount.create(**auth_account_data)
    await user.auth_accounts.add(auth_account)

    access_token: str = await spotify_auth(user_id=str(user.id))

    AssertThat(access_token).IsEqualTo(new_access_token)
