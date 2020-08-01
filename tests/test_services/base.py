"""Base tests utils."""
from typing import Any
from typing import Dict

from httpx import HTTPError
from httpx import Request
from httpx import Response
from orjson import dumps  # pylint: disable-msg=E0611


class ValidResponseMock(Response):
    """External provider response mock."""

    def raise_for_status(self) -> None:
        """Httpx Response raise for status mock."""
        return None


class InvalidResponseMock(Response):
    """External provider response mock."""

    def raise_for_status(self) -> None:
        """Httpx Response raise for status mock."""
        raise HTTPError("test http error", response=self)


def get_response_mock(method: str, response_data: Dict[str, Any], valid: bool):  # type: ignore
    """Response mock factory."""
    response_class = ValidResponseMock if valid is True else InvalidResponseMock
    response = response_class(
        status_code=200,
        content=dumps(response_data),
        request=Request(method=method.upper(), url="http://test.test"),
    )

    return response
