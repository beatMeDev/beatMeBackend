"""Test auth endpoints"""
from typing import Dict
from typing import List
from typing import Tuple

import pytest

from starlette.testclient import TestClient

from app import application


client: TestClient = TestClient(application)

requests: List[Tuple[str, str, Dict[str, str], int]] = [
    ("POST", "/api/auth/facebook/", {}, 400),
    ("GET", "/api/auth/facebook/", {}, 200),
    ("POST", "/api/auth/google/", {}, 400),
    ("GET", "/api/auth/google/", {}, 200),
    ("POST", "/api/auth/spotify/", {}, 400),
    ("GET", "/api/auth/spotify/", {}, 200),
    ("POST", "/api/auth/vk/", {}, 400),
    ("GET", "/api/auth/vk/", {}, 200),
    ("POST", "/api/auth/logout/", {}, 403),
    ("POST", "/api/auth/refresh/", {}, 403),
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

    assert response.status_code == expected_status
