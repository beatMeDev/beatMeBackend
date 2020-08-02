"""Test playlists endpoints"""
from typing import Dict
from typing import List
from typing import Tuple

import pytest

from starlette.testclient import TestClient
from truth.truth import AssertThat  # type: ignore

from app import get_application
from tests.conftest import mock_auth


application = get_application()
client: TestClient = TestClient(application)
application = mock_auth(application)

requests: List[Tuple[str, str, Dict[str, str], int]] = [
    ("POST", "/api/playlists/", {}, 401),
]


@pytest.mark.parametrize(  # pylint: disable=not-callable
    "method,endpoint,data,expected_status", requests
)
def test_endpoint_exists(
        method: str, endpoint: str, data: Dict[str, str], expected_status: int
) -> None:
    """
    Check endpoint exists
    :param method: endpoint method
    :param endpoint: endpoint
    :param expected_status: expected response status code
    :return: nothing
    """
    response = client.request(method=method, url=endpoint, json=data)

    AssertThat(response.status_code).IsEqualTo(expected_status)
