"""Base auth services test."""

import asyncio

from typing import Any
from typing import Dict
from typing import Optional
from typing import Union
from unittest import mock
from unittest.mock import MagicMock
from uuid import UUID

import jwt
import pytest

from fastapi.responses import ORJSONResponse
from orjson import dumps
from orjson import loads
from starlette.datastructures import QueryParams
from starlette.requests import Request

from app.models.api.auth import AuthOut
from app.models.db.user import AuthAccount
from app.models.db.user import User
from app.services.auth.base import OAuthRoute
from app.services.auth.base import create_tokens
from app.services.auth.base import logout
from app.services.auth.base import refresh_tokens
from app.settings import JWT_ALGORITHM
from app.settings import JWT_SECRET


user_uuid = UUID("ef4b35cb-1c32-43b7-a986-14ba5d05064f")
auth_account_id = "1"


async def endpoint_logic() -> None:
    pass


class TestOAuthRoute(OAuthRoute):
    """Test auth class with mocked methods."""

    __test__ = False

    async def code_auth(self, code: str) -> str:
        """
        Code auth mock.

        :param code: auth code
        :return: mock value
        """
        return "access_token"

    async def get_account_info(self, access_token: str) -> Dict[str, str]:
        """Get account info mock."""
        return {"id": auth_account_id, "name": "Test", "image": "link", "url": "link"}


def get_patched_route() -> TestOAuthRoute:
    route = TestOAuthRoute(endpoint=endpoint_logic, path="test")

    return route


async def get_auth_request(user_id: Optional[str] = None) -> Request:
    request_scope = {
        "type": "http",
        "query_params": QueryParams(code="test"),
        "query_string": b"code=test",
        "headers": {},
    }

    if user_id:
        request_scope["user_id"] = user_id

    request = Request(scope=request_scope)

    return request


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
async def test_create_tokens_check_schema(set_mock: MagicMock) -> None:
    """
    Test tokens creation if user id in account info
    """
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(True)

    tokens: Dict[str, Union[str, int]] = await create_tokens(user_id=str(user_uuid))

    assert AuthOut(**tokens).validate(tokens)


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
async def test_create_tokens_check_tokens(set_mock: MagicMock) -> None:
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(True)

    tokens: Dict[str, Union[str, int]] = await create_tokens(user_id=str(user_uuid))

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    access_token_data: Dict[str, Any] = jwt.decode(
        jwt=access_token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )
    refresh_token_data = jwt.decode(
        jwt=refresh_token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )

    assert access_token_data.get("user_id") == str(user_uuid)
    assert refresh_token_data.get("access_token") == access_token


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
async def test_base_auth_route(set_mock: MagicMock) -> None:
    """
    Check auth handler when AuthAccount and User are not exist,
    AuthAccount, User and relation between them should be created,
    tokens should be returned.
    """
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(True)
    route = get_patched_route()
    route_handler = route.get_route_handler()
    request: Request = await get_auth_request()

    response: ORJSONResponse = await route_handler(request)
    response_body = loads(response.body)
    auth_account: AuthAccount = await AuthAccount.get(id=auth_account_id)
    user: User = await User.get(auth_accounts__in=[auth_account])

    assert AuthOut(**response_body).validate(response_body)
    assert auth_account
    assert user


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
@mock.patch("app.extensions.redis_client.get")
@mock.patch("app.extensions.redis_client.delete")
async def test_logout(delete_mock: MagicMock, get_mock: MagicMock, set_mock: MagicMock):
    """
    Check that access token and refresh token will be deleted from redis.
    """
    delete_mock.return_value = asyncio.Future()
    delete_mock.return_value.set_result(True)
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(True)
    tokens: Dict[str, Union[str, int]] = await create_tokens(user_id=str(user_uuid))
    access_token: str = tokens["access_token"]
    refresh_token: str = tokens["refresh_token"]
    get_mock.return_value = asyncio.Future()
    get_mock.return_value.set_result(dumps({"refresh_token": refresh_token}))

    result: bool = await logout(access_token=access_token)

    assert result is True
    delete_mock.assert_any_call(access_token)
    delete_mock.assert_any_call(refresh_token)


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
@mock.patch("app.extensions.redis_client.get")
@mock.patch("app.extensions.redis_client.delete")
async def test_refresh_tokens(
    delete_mock: MagicMock, get_mock: MagicMock, set_mock: MagicMock
):
    """
    Test tokens refreshing
    """
    delete_mock.return_value = asyncio.Future()
    delete_mock.return_value.set_result(True)
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(True)

    tokens: Dict[str, Union[str, int]] = await create_tokens(user_id=str(user_uuid))
    get_mock.return_value = asyncio.Future()
    get_mock.return_value.set_result(
        dumps({"access_token": tokens["access_token"], "user_id": str(user_uuid)})
    )
    refresh_token: str = tokens["refresh_token"]

    new_tokens: Dict[str, Union[str, int]] = await refresh_tokens(
        refresh_token=refresh_token
    )

    assert AuthOut(**new_tokens).validate(new_tokens)


# TODO check account exists and user exists(user_id in scope)
# TODO check account exists and user exists(user_id not in scope)
# TODO check account exists and user not exists
# TODO check relation user and auth account
