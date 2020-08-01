"""Base auth test_services test."""

import asyncio

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from unittest import mock
from unittest.mock import MagicMock
from uuid import UUID

import jwt
import pytest

from fastapi.responses import ORJSONResponse
from orjson import dumps  # pylint: disable-msg=E0611
from orjson import loads  # pylint: disable-msg=E0611
from starlette.datastructures import QueryParams
from starlette.requests import Request
from truth.truth import AssertThat  # type: ignore

from app.models.api.auth import AuthOut
from app.models.db.user import AuthAccount
from app.models.db.user import User
from app.services.auth.base import OAuthRoute
from app.services.auth.base import create_tokens
from app.services.auth.base import logout
from app.services.auth.base import refresh_tokens
from app.settings import JWT_ALGORITHM
from app.settings import JWT_SECRET
from app.utils.exceptions import UnauthorizedError


USER_UUID = UUID("ef4b35cb-1c32-43b7-a986-14ba5d05064f")
AUTH_ACCOUNT_ID = "1"
REDIRECT_LINK = "link"


async def endpoint_logic() -> None:
    """Endpoint logic mock"""
    return None


class TestOAuthRoute(OAuthRoute):
    """Test auth class with mocked methods."""

    __test__ = False

    async def code_auth(self, code: str) -> Tuple[str, str, int]:
        """
        Code auth mock.
        :param code: auth code
        :return: mock value
        """
        return "access_token", "refresh_token", 1000000

    async def get_account_info(self, access_token: str) -> Dict[str, str]:
        """Get account info mock."""
        return {"_id": AUTH_ACCOUNT_ID, "name": "Test", "image": "link", "url": "link"}

    async def create_auth_link(self) -> str:
        """Create link for sign in on external provider."""
        return REDIRECT_LINK


def get_patched_route() -> TestOAuthRoute:
    """Create patched test route."""
    route = TestOAuthRoute(endpoint=endpoint_logic, path="test")

    return route


async def get_auth_request(method: str, user_id: Optional[str] = None) -> Request:
    """Create test request."""
    request_scope = {
        "type": "http",
        "method": method,
        "query_params": QueryParams(code="test"),
        "query_string": b"code=test",
        "headers": [],
    }

    if user_id:
        request_scope["user_id"] = user_id

    request = Request(scope=request_scope)

    return request

not_implemented_methods: List[Any] = [
    ("code_auth", {"code": "test"}, ),
    ("get_account_info", {"access_token": "test"}, ),
    ("create_auth_link", {}, ),
]


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
async def test_create_tokens_check_schema(set_mock: MagicMock) -> None:
    """
    Test tokens creation if user id in account info
    """
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(True)

    tokens: Dict[str, Union[str, int]] = await create_tokens(user_id=str(USER_UUID))

    AssertThat(AuthOut(**tokens).validate(tokens)).IsNotEmpty()  # type: ignore


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
async def test_create_tokens_check_tokens(set_mock: MagicMock) -> None:
    """Check created tokens and encoded data in them."""
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(True)

    tokens: Dict[str, Any] = await create_tokens(user_id=str(USER_UUID))

    access_token: str = tokens["access_token"]
    refresh_token: str = tokens["refresh_token"]
    access_token_data: Dict[str, Any] = jwt.decode(
        jwt=access_token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )
    refresh_token_data = jwt.decode(
        jwt=refresh_token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )

    AssertThat(access_token_data.get("user_id")).IsEqualTo(str(USER_UUID))
    AssertThat(refresh_token_data.get("access_token")).IsEqualTo(access_token)


@pytest.mark.asyncio
@pytest.mark.parametrize(  # pylint: disable=not-callable
    "method_name,methods_kwargs", not_implemented_methods,
)
async def test_base_auth_route_not_implement(
        method_name: str,
        methods_kwargs: Dict[str, Any]
) -> None:
    """Check not implemented methods were raised."""
    route = OAuthRoute(path="/test/", endpoint=endpoint_logic)

    with AssertThat(NotImplementedError).IsRaised():
        await getattr(route, method_name)(**methods_kwargs)


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
async def test_base_auth_route_on_post(set_mock: MagicMock) -> None:
    """
    Check auth handler when AuthAccount and User are not exist,
    AuthAccount, User and relation between them should be created,
    tokens should be returned.
    """
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(True)
    route = get_patched_route()
    route_handler = route.get_route_handler()
    request: Request = await get_auth_request(method="POST")

    response: ORJSONResponse = await route_handler(request)
    response_body = loads(response.body)
    auth_account: AuthAccount = await AuthAccount.get(_id=AUTH_ACCOUNT_ID)
    user: User = await User.get(auth_accounts__in=[auth_account])

    AssertThat(AuthOut(**response_body).validate(response_body)).IsNotEmpty()
    AssertThat(auth_account).IsNotNone()
    AssertThat(user).IsNotNone()


@pytest.mark.asyncio
async def test_base_auth_route_on_get() -> None:
    """
    Check auth handler on GET will return sign in link for external provider.
    """
    route = get_patched_route()
    route_handler = route.get_route_handler()
    request: Request = await get_auth_request(method="GET")

    response: ORJSONResponse = await route_handler(request)
    response_body = loads(response.body)

    AssertThat(response.status_code).IsEqualTo(200)
    AssertThat(response_body).IsEqualTo({"link": REDIRECT_LINK})


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
@mock.patch("app.extensions.redis_client.get")
@mock.patch("app.extensions.redis_client.delete")
async def test_logout(
        delete_mock: MagicMock, get_mock: MagicMock, set_mock: MagicMock
) -> None:
    """
    Check that access token and refresh token will be deleted from redis.
    """
    delete_mock.return_value = asyncio.Future()
    delete_mock.return_value.set_result(True)
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(True)
    tokens: Dict[str, Any] = await create_tokens(user_id=str(USER_UUID))
    access_token: str = tokens["access_token"]
    refresh_token: str = tokens["refresh_token"]
    get_mock.return_value = asyncio.Future()
    get_mock.return_value.set_result(dumps({"refresh_token": refresh_token}))

    result: bool = await logout(access_token=access_token)

    AssertThat(result).IsTrue()
    delete_mock.assert_any_call(access_token)
    delete_mock.assert_any_call(refresh_token)


@pytest.mark.asyncio
async def test_logout_token_is_none() -> None:
    """
    Check logout if token is none.
    """
    result: bool = await logout(access_token=None)

    AssertThat(result).IsFalse()


@mock.patch("app.extensions.redis_client.get")
@pytest.mark.asyncio
async def test_logout_data_is_none(get_mock: MagicMock) -> None:
    """
    Check logout if toke_data is none.
    """
    get_mock.return_value = asyncio.Future()
    get_mock.return_value.set_result(None)

    result: bool = await logout(access_token="test_token")

    AssertThat(result).IsFalse()


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.set")
@mock.patch("app.extensions.redis_client.get")
@mock.patch("app.extensions.redis_client.delete")
async def test_refresh_tokens(
        delete_mock: MagicMock, get_mock: MagicMock, set_mock: MagicMock
) -> None:
    """
    Test tokens refreshing if everything is fine.
    """
    delete_mock.return_value = asyncio.Future()
    delete_mock.return_value.set_result(True)
    set_mock.return_value = asyncio.Future()
    set_mock.return_value.set_result(True)

    tokens: Dict[str, Any] = await create_tokens(user_id=str(USER_UUID))
    get_mock.return_value = asyncio.Future()
    get_mock.return_value.set_result(
        dumps({"access_token": tokens["access_token"], "user_id": str(USER_UUID)})
    )
    refresh_token: str = tokens["refresh_token"]

    new_tokens: Dict[str, Union[str, int]] = await refresh_tokens(
        refresh_token=refresh_token
    )

    AssertThat(AuthOut(**new_tokens).validate(new_tokens)).IsNotEmpty()  # type: ignore


@pytest.mark.asyncio
@mock.patch("app.extensions.redis_client.get")
async def test_refresh_tokens_not_raw_token(get_mock: MagicMock) -> None:
    """
    Test tokens refreshing if token not exists in redis storage.
    """
    get_mock.return_value = asyncio.Future()
    get_mock.return_value.set_result(None)

    with AssertThat(UnauthorizedError).IsRaised():
        await refresh_tokens(refresh_token="test_token")


@pytest.mark.asyncio
@mock.patch("app.services.auth.base.logout")
@mock.patch("app.extensions.redis_client.get")
async def test_refresh_tokens_logout_false(
        get_mock: MagicMock,
        logout_mock: MagicMock,
) -> None:
    """
    Test tokens refreshing if logout returned False.
    """
    get_mock.return_value = asyncio.Future()
    get_mock.return_value.set_result(
        dumps({"access_token": "test_token"})
    )
    logout_mock.return_value = False

    with AssertThat(UnauthorizedError).IsRaised():
        await refresh_tokens(refresh_token="test_token")
