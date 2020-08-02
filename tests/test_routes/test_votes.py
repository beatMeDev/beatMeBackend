"""Test votes endpoints"""

from starlette.testclient import TestClient
from truth.truth import AssertThat  # type: ignore

from app import get_application
from tests.conftest import POPULATE_SUBMISSION_ID
from tests.conftest import mock_auth


application = get_application()
client: TestClient = TestClient(application)
application = mock_auth(application)


def test_vote_challenge_in_progress(  # type: ignore
        user_fixture,  # pylint: disable=unused-argument
        submission_fixture,  # pylint: disable=unused-argument
) -> None:
    """Check vote when challenge in process."""
    method, endpoint, data, expected_status = (
        "POST",
        "/api/votes/",
        {"submission_id": str(POPULATE_SUBMISSION_ID)},
        400,
    )
    response = client.request(
        method=method,
        url=endpoint,
        json=data,
    )

    AssertThat(response.status_code).IsEqualTo(expected_status)


def test_vote_challenge_ended(  # type: ignore
        user_fixture,  # pylint: disable=unused-argument
        submission_ended_fixture,  # pylint: disable=unused-argument
) -> None:
    """Check vote when challenge ended."""
    method, endpoint, data, expected_status = (
        "POST",
        "/api/votes/",
        {"submission_id": str(POPULATE_SUBMISSION_ID)},
        400,
    )
    response = client.request(
        method=method,
        url=endpoint,
        json=data,
    )

    AssertThat(response.status_code).IsEqualTo(expected_status)


def test_vote_challenge_voting(  # type: ignore
        user_fixture,  # pylint: disable=unused-argument
        submission_vote_fixture,  # pylint: disable=unused-argument
) -> None:
    """Check vote when challenge on voting."""
    method, endpoint, data, expected_status = (
        "POST",
        "/api/votes/",
        {"submission_id": str(POPULATE_SUBMISSION_ID)},
        200,
    )
    response = client.request(
        method=method,
        url=endpoint,
        json=data,
    )

    AssertThat(response.status_code).IsEqualTo(expected_status)


def test_vote_exists(  # type: ignore
        user_fixture,  # pylint: disable=unused-argument
        vote_fixture,  # pylint: disable=unused-argument
) -> None:
    """Check vote when challenge on voting and vote exists."""
    method, endpoint, data, expected_status = (
        "POST",
        "/api/votes/",
        {"submission_id": str(POPULATE_SUBMISSION_ID)},
        200,
    )
    response = client.request(
        method=method,
        url=endpoint,
        json=data,
    )

    AssertThat(response.status_code).IsEqualTo(expected_status)
