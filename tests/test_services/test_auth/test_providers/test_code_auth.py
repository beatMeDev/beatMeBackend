"""
Test code_auth methods in external providers.
"""
from datetime import datetime
from typing import Any
from typing import Dict
from unittest import mock
from unittest.mock import MagicMock

import pytest

from freezegun import freeze_time  # type: ignore
from httpx import HTTPError
from httpx import Request
from httpx import Response
from orjson import dumps  # pylint: disable-msg=E0611
from truth.truth import AssertThat  # type: ignore

from app.services.auth import FacebookAuth
from app.services.auth import GoogleAuth
from app.services.auth import SpotifyAuth
from app.services.auth import VKAuth
from app.utils.exceptions import UnauthorizedError
from tests.test_services.test_auth.test_base import endpoint_logic


class ValidResponseMock(Response):
    """External provider response mock."""

    def raise_for_status(self) -> None:
        """Httpx Response raise for status mock."""
        return None


class InvalidResponseMock(Response):
    """External provider response mock."""

    def raise_for_status(self) -> None:
        """Httpx Response raise for status mock."""
        raise HTTPError("test http error", response=self)


def get_response_mock(method: str, response_data: Dict[str, Any], valid: bool):  # type: ignore
    """Response mock factory."""
    response_class = ValidResponseMock if valid is True else InvalidResponseMock
    response = response_class(
        status_code=200,
        content=dumps(response_data),
        request=Request(method=method.upper(), url="http://test.test"),
    )

    return response


facebook_response_data: Dict[str, Any] = {
    "access_token": "test_access",
    "refresh_token": "",
    "expires_in": 1,
}
google_response_data: Dict[str, Any] = {
    "access_token": "test_access",
    "refresh_token": "test_refresh",
    "expires_in": 1,
}
spotify_response_data: Dict[str, Any] = {
    "access_token": "test_access",
    "refresh_token": "test_refresh",
    "expires_in": 1,
}
vk_response_data: Dict[str, Any] = {
    "access_token": "test_access",
    "refresh_token": "",
    "expires_in": 1,
}

fixtures = [
    (FacebookAuth, facebook_response_data),
    (GoogleAuth, google_response_data),
    (SpotifyAuth, spotify_response_data),
    (VKAuth, vk_response_data),
]


@pytest.mark.asyncio
@freeze_time("1970-01-01")
@pytest.mark.parametrize(  # pylint: disable=not-callable
    "provider,response_data", fixtures
)
@mock.patch("app.extensions.http_client.get")
@mock.patch("app.extensions.http_client.post")
async def test_code_auth_valid_response(  # type: ignore
        response_post_mock: MagicMock,
        response_get_mock: MagicMock,
        provider,
        response_data: Dict[str, Any],
) -> None:
    """Check code auth method in provider if response is valid."""
    response_get_mock.return_value = get_response_mock(
        method="GET", response_data=response_data, valid=True,
    )
    response_post_mock.return_value = get_response_mock(
        method="POST", response_data=response_data, valid=True,
    )

    route = provider(endpoint=endpoint_logic, path="/test/")
    access_token, refresh_token, expires = await route.code_auth(code="test")

    AssertThat(access_token).IsEqualTo(response_data["access_token"])
    AssertThat(refresh_token).IsEqualTo(response_data["refresh_token"])
    AssertThat(expires).IsEqualTo(
        response_data["expires_in"] + int(datetime.utcnow().timestamp())
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(  # pylint: disable=not-callable
    "provider,response_data", fixtures
)
@mock.patch("app.extensions.http_client.get")
@mock.patch("app.extensions.http_client.post")
async def test_code_auth_invalid_response(  # type: ignore
        response_post_mock: MagicMock,
        response_get_mock: MagicMock,
        provider,
        response_data: Dict[str, Any],
) -> None:
    """Check code auth method in provider if response is not valid."""
    response_get_mock.return_value = get_response_mock(
        method="GET", response_data=response_data, valid=False,
    )
    response_post_mock.return_value = get_response_mock(
        method="POST", response_data=response_data, valid=False,
    )

    with AssertThat(UnauthorizedError).IsRaised():
        route = provider(endpoint=endpoint_logic, path="/test/")
        await route.code_auth(code="test")
