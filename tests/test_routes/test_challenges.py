"""Test challenges endpoints"""
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import pytest

from freezegun import freeze_time  # type: ignore
from starlette.testclient import TestClient
from truth.truth import AssertThat  # type: ignore

from app import get_application
from app.services.auth.base import bearer_auth
from tests.conftest import POPULATE_TRACK_ID
from tests.test_services.test_auth.test_base import USER_UUID


async def bearer_auth_mock() -> str:
    """Auth method mock."""
    return str(USER_UUID)


application = get_application()
client: TestClient = TestClient(application)

# Mock auth dependency and token middleware
application.dependency_overrides[bearer_auth] = bearer_auth_mock

application.user_middleware = []
application.middleware_stack = application.build_middleware_stack()

valid_challenge_data: Dict[str, Any] = {
    "name": "string",
    "challenge_end": "2020-01-01T00:00:00.000Z",
    "vote_end": "2020-01-02T00:00:00.000Z",
    "is_public": True,
    "is_open": True,
    "track_id": POPULATE_TRACK_ID,
}
challenge_data_challenge_end_invalid = {
    **valid_challenge_data,
    "challenge_end": "2018-01-01T00:00:00.000Z",
}
challenge_data_vote_end_less_start = {
    **valid_challenge_data,
    "challenge_end": "2020-01-02:00:00.000Z",
    "vote_end": "2020-01-01T00:00:00.000Z",
}
challenge_data_empty_name = {
    **valid_challenge_data,
    "name": "",
}

requests: List[Tuple[str, str, Dict[str, str], int]] = [
    ("POST", "/api/challenges/", valid_challenge_data, 200),
    ("POST", "/api/challenges/", challenge_data_challenge_end_invalid, 422),
    ("POST", "/api/challenges/", challenge_data_vote_end_less_start, 422),
    ("POST", "/api/challenges/", challenge_data_empty_name, 422),
    ("GET", "/api/challenges/", {}, 200),
    ("GET", "/api/challenges/my/", {}, 200),
    ("GET", "/api/challenges/participant/", {}, 200),
]


@freeze_time("2019-01-01")
@pytest.mark.parametrize(  # pylint: disable=not-callable
    "method,endpoint,data,expected_status", requests
)  # pylint: disable=too-many-arguments
def test_endpoint_exists(  # type: ignore
        method: str,
        endpoint: str,
        data: Dict[str, str],
        expected_status: int,
        populate_user,  # pylint: disable=unused-argument
        populate_playlist_with_track,  # pylint: disable=unused-argument
) -> None:
    """
    Check endpoint exists
    :param method: endpoint method
    :param endpoint: endpoint
    :param expected_status: expected response status code
    :return: nothing
    """
    response = client.request(
        method=method,
        url=endpoint,
        json=data,
    )

    AssertThat(response.status_code).IsEqualTo(expected_status)
