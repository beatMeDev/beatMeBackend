"""Test challenges endpoints"""
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import pytest

from starlette.testclient import TestClient
from truth.truth import AssertThat  # type: ignore

from app import get_application
from tests.conftest import POPULATE_CHALLENGE_FOREIGN_ID as FOREIGN_ID
from tests.conftest import POPULATE_CHALLENGE_FOREIGN_SECRET as FOREIGN_SECRET
from tests.conftest import POPULATE_CHALLENGE_ID
from tests.conftest import POPULATE_CHALLENGE_SECRET
from tests.conftest import POPULATE_TRACK_ID
from tests.conftest import mock_auth


application = get_application()
client: TestClient = TestClient(application)
application = mock_auth(application)

date_format: str = "%Y-%m-%dT%H:%M:%S.000Z"
valid_challenge_data: Dict[str, Any] = {
    "name": "string",
    "challenge_end": (datetime.utcnow() + timedelta(hours=1)).strftime(date_format),
    "vote_end": (datetime.utcnow() + timedelta(hours=2)).strftime(date_format),
    "is_public": True,
    "is_open": True,
    "track_id": POPULATE_TRACK_ID,
}
challenge_data_challenge_end_invalid = {
    **valid_challenge_data,
    "challenge_end": (datetime.utcnow() - timedelta(days=1)).strftime(date_format),
}
challenge_data_vote_end_less_start = {
    **valid_challenge_data,
    "challenge_end": (datetime.utcnow() + timedelta(hours=2)).strftime(date_format),
    "vote_end": (datetime.utcnow() + timedelta(hours=1)).strftime(date_format),
}
challenge_data_empty_name = {
    **valid_challenge_data,
    "name": "",
}

submit_valid_data: Dict[str, str] = {
    "url": "https://soundcloud.com/test/test",
}
submit_invalid_data: Dict[str, str] = {
    "url": "https://google.com/"
}

requests: List[Tuple[str, str, Dict[str, str], int]] = [
    ("POST", "/api/challenges/", valid_challenge_data, 200),
    ("POST", f"/api/challenges/{str(POPULATE_CHALLENGE_ID)}/accept/", {}, 200),
    ("GET", f"/api/challenges/{str(POPULATE_CHALLENGE_ID)}/participants/", {}, 200),
    ("POST", f"/api/challenges/{str(POPULATE_CHALLENGE_ID)}/submit/", submit_valid_data, 200),
    ("POST", f"/api/challenges/{str(POPULATE_CHALLENGE_ID)}/submit/", submit_invalid_data, 422),
    ("GET", f"/api/challenges/{str(POPULATE_CHALLENGE_ID)}/submissions/", {}, 200),
    ("GET", f"/api/challenges/{str(POPULATE_CHALLENGE_ID)}/", {}, 200),
    ("POST", "/api/challenges/", challenge_data_challenge_end_invalid, 422),
    ("POST", "/api/challenges/", challenge_data_vote_end_less_start, 422),
    ("POST", "/api/challenges/", challenge_data_empty_name, 422),
    ("GET", "/api/challenges/", {}, 200),
    ("GET", "/api/challenges/my/", {}, 200),
    ("GET", "/api/challenges/participant/", {}, 200),
]


@pytest.mark.parametrize(  # pylint: disable=not-callable
    "method,endpoint,data,expected_status", requests
)  # pylint: disable=too-many-arguments
def test_endpoint_exists(  # type: ignore
        method: str,
        endpoint: str,
        data: Dict[str, str],
        expected_status: int,
        user_fixture,  # pylint: disable=unused-argument
        challenge_process_fixture,  # pylint: disable=unused-argument
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


secret_no_access_requests: List[Tuple[str, str, Dict[str, str], int]] = [
    ("GET", f"/api/challenges/{str(FOREIGN_ID)}/?secret=trash", {}, 403),
    ("POST", f"/api/challenges/{str(FOREIGN_ID)}/accept/?secret=trash", {}, 403),
    ("POST", f"/api/challenges/{str(FOREIGN_ID)}/submit/?secret=trash", submit_valid_data, 403),
]


@pytest.mark.parametrize(  # pylint: disable=not-callable
    "method,endpoint,data,expected_status", secret_no_access_requests
)  # pylint: disable=too-many-arguments
def test_secret_without_access(  # type: ignore
        method: str,
        endpoint: str,
        data: Dict[str, str],
        expected_status: int,
        user_fixture,  # pylint: disable=unused-argument
        challenge_foreign_fixture,  # pylint: disable=unused-argument
) -> None:
    """Check endpoints when user has no access and secret."""
    response = client.request(
        method=method,
        url=endpoint,
        json=data,
        params={"secret": "trash"}
    )

    AssertThat(response.status_code).IsEqualTo(expected_status)


secret_with_access_requests: List[Tuple[str, str, Dict[str, str], int]] = [
    ("GET", f"/api/challenges/{str(FOREIGN_ID)}/", {}, 200),
    ("POST", f"/api/challenges/{str(FOREIGN_ID)}/accept/", {}, 200),
    ("POST", f"/api/challenges/{str(FOREIGN_ID)}/submit/", submit_valid_data, 200),
]


@pytest.mark.parametrize(  # pylint: disable=not-callable
    "method,endpoint,data,expected_status", secret_with_access_requests
)  # pylint: disable=too-many-arguments
def test_secret_with_access(  # type: ignore
        method: str,
        endpoint: str,
        data: Dict[str, str],
        expected_status: int,
        user_fixture,  # pylint: disable=unused-argument
        challenge_foreign_fixture,  # pylint: disable=unused-argument
) -> None:
    """Check endpoints when user has access and secret."""
    response = client.request(
        method=method,
        url=endpoint,
        json=data,
        params={"secret": str(FOREIGN_SECRET)}
    )

    AssertThat(response.status_code).IsEqualTo(expected_status)


ended_requests: List[Tuple[str, str, Dict[str, str], int]] = [
    ("POST", f"/api/challenges/{str(POPULATE_CHALLENGE_ID)}/accept/", {}, 403),
    ("POST", f"/api/challenges/{str(POPULATE_CHALLENGE_ID)}/submit/", submit_valid_data, 403),
]


@pytest.mark.parametrize(  # pylint: disable=not-callable
    "method,endpoint,data,expected_status", ended_requests
)  # pylint: disable=too-many-arguments
def test_ended_challenge(  # type: ignore
        method: str,
        endpoint: str,
        data: Dict[str, str],
        expected_status: int,
        user_fixture,  # pylint: disable=unused-argument
        challenge_end_fixture,  # pylint: disable=unused-argument
) -> None:
    """Check endpoints when challenge is ended."""
    response = client.request(
        method=method,
        url=endpoint,
        json=data,
        params={"secret": str(POPULATE_CHALLENGE_SECRET)}
    )

    AssertThat(response.status_code).IsEqualTo(expected_status)


submission_requests = [
    ("POST", f"/api/challenges/{str(POPULATE_CHALLENGE_ID)}/submit/", submit_valid_data, 200),
]


@pytest.mark.parametrize(  # pylint: disable=not-callable
    "method,endpoint,data,expected_status", submission_requests
)  # pylint: disable=too-many-arguments
def test_exist_submission(  # type: ignore
        method: str,
        endpoint: str,
        data: Dict[str, str],
        expected_status: int,
        user_fixture,  # pylint: disable=unused-argument
        submission_fixture,  # pylint: disable=unused-argument
) -> None:
    """Check endpoints when submission exists."""
    response = client.request(
        method=method,
        url=endpoint,
        json=data,
        params={"secret": str(POPULATE_CHALLENGE_SECRET)}
    )

    AssertThat(response.status_code).IsEqualTo(expected_status)
