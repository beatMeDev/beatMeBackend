"""Tests for VK auth provider."""
from typing import Any
from typing import Dict
from unittest import mock
from unittest.mock import MagicMock

import pytest

from truth.truth import AssertThat  # type: ignore

from app.services.auth import VKAuth
from app.utils.exceptions import UnauthorizedError
from tests.test_services.base import get_response_mock
from tests.test_services.test_auth.test_base import endpoint_logic


@pytest.mark.asyncio
@mock.patch("app.extensions.http_client.get")
async def test_get_account_info_empty_response(
        response_get_mock: MagicMock,
) -> None:
    """Check get_account_info method in vk if empty response."""
    response_data: Dict[str, Any] = {}
    response_get_mock.return_value = get_response_mock(
        method="GET", response_data=response_data, valid=True,
    )

    with AssertThat(UnauthorizedError).IsRaised():
        route = VKAuth(endpoint=endpoint_logic, path="/test/")
        await route.get_account_info(access_token="test")
