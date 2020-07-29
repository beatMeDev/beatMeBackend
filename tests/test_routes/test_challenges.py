"""Test challenges endpoints"""
from typing import List, Tuple, Dict

import pytest
from starlette.testclient import TestClient

from app import application

client: TestClient = TestClient(application)

requests: List[Tuple[str, str, Dict[str, str], int]] = [
    ("POST", "/api/challenges/", {}, 403),
    ("GET", "/api/challenges/", {}, 200),
    ("GET", "/api/challenges/my/", {}, 403),
    ("GET", "/api/challenges/participant/", {}, 403),
]


@pytest.mark.parametrize("method,endpoint,data,expected_status", requests)
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