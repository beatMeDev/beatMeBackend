"""
Test get_account_info methods in external providers.
"""
from typing import Any
from typing import Dict
from unittest import mock
from unittest.mock import MagicMock

import pytest

from truth.truth import AssertThat  # type: ignore

from app.services.auth import FacebookAuth
from app.services.auth import GoogleAuth
from app.services.auth import SpotifyAuth
from app.services.auth import VKAuth
from app.utils.exceptions import UnauthorizedError
from tests.test_services.base import get_response_mock
from tests.test_services.test_auth.test_base import endpoint_logic


test_id: str = "test_id"
test_first_name: str = "test_first"
test_last_name: str = "test_last"
test_image: str = "test_image"
test_url: str = "test_url"

expected_data_fixture: Dict[str, str] = {
    "_id": test_id,
    "name": f"{test_first_name} {test_last_name}",
    "image": test_image,
    "url": test_url,
}

facebook_response_data: Dict[str, Any] = {
    "id": test_id,
    "first_name": test_first_name,
    "last_name": test_last_name,
    "picture": {"data": {"url": test_image}},
    "link": test_url,
}
google_response_data: Dict[str, Any] = {
    "sub": test_id,
    "name": f"{test_first_name} {test_last_name}",
    "picture": test_image,
    "link": test_url,
}
spotify_response_data: Dict[str, Any] = {
    "id": test_id,
    "display_name": f"{test_first_name} {test_last_name}",
    "images": [{"url": test_image}],
    "external_urls": {"spotify": test_url},
}
vk_response_data: Dict[str, Any] = {
    "response": [
        {
            "id": test_id,
            "first_name": test_first_name,
            "last_name": test_last_name,
            "photo_400_orig": test_image,
        }
    ]
}

fixtures = [
    (FacebookAuth, facebook_response_data, expected_data_fixture),
    (GoogleAuth, google_response_data, expected_data_fixture),
    (SpotifyAuth, spotify_response_data, expected_data_fixture),
    (VKAuth, vk_response_data, expected_data_fixture),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(  # pylint: disable=not-callable
    "provider,response_data,expected_data", fixtures
)
@mock.patch("app.extensions.http_client.get")
async def test_get_account_info_valid_response(  # type: ignore
        response_get_mock: MagicMock,
        provider,
        response_data: Dict[str, Any],
        expected_data: Dict[str, Any],
) -> None:
    """Check get_account_info method in provider if response is valid."""
    response_get_mock.return_value = get_response_mock(
        method="GET", response_data=response_data, valid=True,
    )

    route = provider(endpoint=endpoint_logic, path="/test/")
    info: Dict[str, str] = await route.get_account_info(access_token="test")

    AssertThat(info["_id"]).IsEqualTo(expected_data["_id"])
    AssertThat(info["name"]).IsEqualTo(expected_data["name"])
    AssertThat(info["image"]).IsEqualTo(expected_data["image"])
    AssertThat(info["url"]).ContainsAnyIn(expected_data["url"])


@pytest.mark.asyncio
@pytest.mark.parametrize(  # pylint: disable=not-callable
    "provider,response_data,expected_data", fixtures
)
@mock.patch("app.extensions.http_client.get")
async def test_get_account_info_invalid_response(  # type: ignore
        response_get_mock: MagicMock,
        provider,
        response_data: Dict[str, Any],
        expected_data: Dict[str, Any],  # pylint: disable=unused-argument
) -> None:
    """Check get_account_info method in provider if response is not valid."""
    response_get_mock.return_value = get_response_mock(
        method="GET", response_data=response_data, valid=False,
    )

    with AssertThat(UnauthorizedError).IsRaised():
        route = provider(endpoint=endpoint_logic, path="/test/")
        await route.get_account_info(access_token="test")
