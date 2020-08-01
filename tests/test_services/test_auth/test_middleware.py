"""Auth middleware tests."""
import asyncio

from typing import Any
from typing import Dict
from typing import Optional
from typing import Union
from unittest import mock
from unittest.mock import MagicMock

import pytest

from fastapi import FastAPI
from orjson import dumps  # pylint: disable-msg=E0611
from starlette.requests import Request
from starlette.responses import Response
from truth.truth import AssertThat  # type: ignore

from app.services.auth.base import create_tokens
from app.services.auth.middleware import TokenAuthMiddleware
from app.utils.exceptions import UnauthorizedError
from tests.test_services.test_auth.test_base import USER_UUID


def request_factory(token: Optional[Any] = None) -> Request:
    """Create test request."""
    request_scope: Dict[str, Any] = {
        "type": "http",
        "method": "GET",
        "headers": [],
    }

    if token is not None:
        request_scope["headers"] = [
            (b"authorization", f"Bearer {token}".encode("utf-8"),)
        ]

    request: Request = Request(scope=request_scope)

    return request


async def call_next(request: Request) -> Response:  # pylint: disable=unused-argument
    """Mock call next method which will be called in middleware."""
    return Response(status_code=200, content=b"test_call_next")


@pytest.mark.asyncio
async def test_auth_middleware_not_authorization() -> None:
    """Check auth middleware if Authorization header is not provided."""
    middleware = TokenAuthMiddleware(app=FastAPI())
    request: Request = request_factory()

    response: Response = await middleware.dispatch(request=request, call_next=call_next)

    call_next_response: Response = await call_next(request=request)
    AssertThat(response.body).IsEqualTo(call_next_response.body)


@pytest.mark.asyncio
async def test_auth_middleware_not_token_in_header() -> None:
    """Check auth middleware if token not provided in header."""
    middleware = TokenAuthMiddleware(app=FastAPI())
    request: Request = request_factory(token="")

    response: Response = await middleware.dispatch(request=request, call_next=call_next)

    call_next_response: Response = await call_next(request=request)
    AssertThat(response.body).IsEqualTo(call_next_response.body)


@pytest.mark.asyncio
async def test_auth_middleware_invalid_token() -> None:
    """Check auth middleware if token is not valid."""
    middleware = TokenAuthMiddleware(app=FastAPI())
    request: Request = request_factory(token="invalid")

    response: Response = await middleware.dispatch(request=request, call_next=call_next)

    AssertThat(response.status_code).IsEqualTo(UnauthorizedError.status_code)


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
@mock.patch("app.extensions.redis_client.get")
async def test_auth_middleware_raw_data_is_none(
        get_mock: MagicMock,
        set_mock: MagicMock,
) -> None:
    """Check auth middleware if tokens raw data from redis is None."""
    get_mock.return_value = asyncio.Future()
    get_mock.return_value.set_result(None)
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(None)
    middleware = TokenAuthMiddleware(app=FastAPI())
    tokens: Dict[str, Union[str, int]] = await create_tokens(user_id=str(USER_UUID))
    request: Request = request_factory(token=tokens["access_token"])

    response: Response = await middleware.dispatch(request=request, call_next=call_next)

    AssertThat(response.status_code).IsEqualTo(UnauthorizedError.status_code)
    get_mock.assert_called_once_with(tokens["access_token"])


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
@mock.patch("app.extensions.redis_client.get")
async def test_auth_middleware(
        get_mock: MagicMock,
        set_mock: MagicMock,
) -> None:
    """Check auth middleware if everything is fine."""
    get_mock.return_value = asyncio.Future()
    get_mock.return_value.set_result(dumps({"user_id": str(USER_UUID), "test": "test"}))
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(None)
    tokens: Dict[str, Union[str, int]] = await create_tokens(user_id=str(USER_UUID))

    middleware = TokenAuthMiddleware(app=FastAPI())
    request: Request = request_factory(token=tokens["access_token"])

    response: Response = await middleware.dispatch(request=request, call_next=call_next)
    call_next_response: Response = await call_next(request=request)

    get_mock.assert_called_once_with(tokens["access_token"])
    AssertThat(response.body).IsEqualTo(call_next_response.body)
