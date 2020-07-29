"""Test auth endpoints"""
from typing import List, Tuple, Dict

import pytest
from starlette.testclient import TestClient

from app import application

client: TestClient = TestClient(application)

requests: List[Tuple[str, str, Dict[str, str], int]] = [
    ("POST", "/api/auth/facebook/", {}, 422),
    ("POST", "/api/auth/google/", {}, 422),
    ("POST", "/api/auth/spotify/", {}, 422),
    ("POST", "/api/auth/vk/", {}, 422),
    ("POST", "/api/auth/logout/", {}, 403),
    ("POST", "/api/auth/refresh/", {}, 403),
]


@pytest.mark.parametrize("method,endpoint,data,expected_status", requests)  # pylint: disable=not-callable
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
