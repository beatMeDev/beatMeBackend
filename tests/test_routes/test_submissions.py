"""Test submissions endpoints"""
from typing import Dict
from typing import List
from typing import Tuple

import pytest

from starlette.testclient import TestClient
from truth.truth import AssertThat  # type: ignore

from app import get_application
from tests.conftest import POPULATE_SUBMISSION_ID
from tests.conftest import mock_auth


application = get_application()
client: TestClient = TestClient(application)
application = mock_auth(application)

submission_requests: List[Tuple[str, str, Dict[str, str], int]] = [
    ("GET", f"/api/submissions/{str(POPULATE_SUBMISSION_ID)}/votes/", {}, 200),
    ("GET", f"/api/submissions/{str(POPULATE_SUBMISSION_ID)}/", {}, 200),
]


@pytest.mark.parametrize(  # pylint: disable=not-callable
    "method,endpoint,data,expected_status", submission_requests
)  # pylint: disable=too-many-arguments
def test_endpoints(  # type: ignore
        method: str,
        endpoint: str,
        data: Dict[str, str],
        expected_status: int,
        user_fixture,  # pylint: disable=unused-argument
        submission_fixture,  # pylint: disable=unused-argument
) -> None:
    """Check endpoints."""
    response = client.request(
        method=method,
        url=endpoint,
        json=data,
    )

    AssertThat(response.status_code).IsEqualTo(expected_status)
