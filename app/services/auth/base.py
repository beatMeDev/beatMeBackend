"""
Base auth services
"""
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

import jwt

from fastapi import Depends
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from orjson import dumps  # pylint: disable-msg=E0611
from orjson import loads  # pylint: disable-msg=E0611
from starlette.requests import Request
from starlette.responses import Response

from app.extensions import redis_client
from app.models.db.user import AuthAccount
from app.models.db.user import AuthProvider
from app.models.db.user import User
from app.settings import ACCESS_TOKEN_LIFETIME
from app.settings import JWT_ALGORITHM
from app.settings import JWT_SECRET
from app.settings import REFRESH_TOKEN_LIFETIME
from app.utils.exceptions import BadRequestError
from app.utils.exceptions import UnauthorizedError


class OAuthRoute(APIRoute):
    """
    Base OAuth fastapi route class.

    get_route_handler - main auth logic,
    code_auth and get_account_info should be implemented in third party providers.
    """

    provider = AuthProvider.DEFAULT
    auth_endpoint: str = ""
    account_endpoint: str = ""
    sign_in_endpoint: str = ""

    async def code_auth(self, code: str) -> Tuple[str, str, int]:
        """
        Exchange code to access token
        :param code: authorization code
        :return: access token, refresh token, when token expires in timestamp
        """
        raise NotImplementedError

    async def get_account_info(self, access_token: str) -> Dict[str, str]:
        """
        Get profile information
        :param access_token: auth service token
        :return: profile information: {"id": "1", "name": "Test", "image": "link", "url": "link"}
        """
        raise NotImplementedError

    async def create_auth_link(self) -> str:
        """
        Create link for user sign in on external provider.
        :return: {"link": link}
        """
        raise NotImplementedError

    async def handle_post(self, request: Request) -> ORJSONResponse:
        """On POST works sign in logic."""
        code: Optional[str] = request.query_params.get("code")

        if not code:
            raise BadRequestError

        user_id: Optional[str] = request.scope.get("user_id")
        access_token, refresh_token, expires = await self.code_auth(code=code)
        account_info: Dict[str, Any] = await self.get_account_info(
            access_token=access_token
        )
        account_info["provider"] = self.provider
        account_info["access_token"] = access_token
        account_info["refresh_token"] = refresh_token
        account_info["expires"] = expires

        auth_account: Optional[AuthAccount] = await AuthAccount.filter(
            _id=account_info["_id"]
        ).first().prefetch_related("user")

        user: Optional[User] = await User.get(id=user_id) if user_id else None

        if auth_account:
            await auth_account.update_from_dict(data=account_info)
            await auth_account.save()
        else:
            if not user:
                user = await User.create()

            auth_account = await AuthAccount.create(**account_info, user=user)

        tokens: Dict[str, Union[str, int]] = await create_tokens(
            user_id=str(auth_account.user.id)  # type: ignore
        )

        return ORJSONResponse(tokens)

    async def handle_get(self) -> ORJSONResponse:
        """On GET generating sign in link on external provider."""
        link: str = await self.create_auth_link()
        response: ORJSONResponse = ORJSONResponse({"link": link})

        return response

    def get_route_handler(self) -> Callable:  # type: ignore
        original_route_handler: Callable = super().get_route_handler()  # type: ignore

        async def custom_route_handler(request: Request) -> Response:
            await original_route_handler(request)

            if request.method.upper() == "GET":
                return await self.handle_get()

            if request.method.upper() == "POST":
                return await self.handle_post(request=request)

            raise BadRequestError

        return custom_route_handler


async def create_tokens(user_id: str) -> Dict[str, Union[str, int]]:
    """
    Create auth tokens
    :param user_id: user's id
    :return: tokens pair and access expire: {
                                                "access_token": "str",
                                                "refresh_token": "str",
                                                "expires_at": "int"
                                            }
    """
    access_expires_at: int = int(
        (datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_LIFETIME)).timestamp()
    )
    refresh_expires_at: int = int(
        (datetime.utcnow() + timedelta(seconds=REFRESH_TOKEN_LIFETIME)).timestamp()
    )
    access_token_body: Dict[str, Union[str, int]] = {
        "user_id": user_id,
        "exp": access_expires_at,
    }
    access_token: str = jwt.encode(
        payload=access_token_body, key=JWT_SECRET, algorithm=JWT_ALGORITHM
    ).decode("utf-8")
    refresh_token_body: Dict[str, Union[str, int]] = {
        "access_token": access_token,
        "exp": refresh_expires_at,
    }
    refresh_token: str = jwt.encode(
        payload=refresh_token_body, key=JWT_SECRET, algorithm=JWT_ALGORITHM
    ).decode("utf-8")
    access_token_data: Dict[str, Union[str, int]] = {
        "user_id": user_id,
        "exp": access_expires_at,
        "refresh_token": refresh_token,
    }
    refresh_token_data: Dict[str, Union[str, int]] = {
        "user_id": user_id,
        "exp": refresh_expires_at,
        "access_token": access_token,
    }

    await redis_client.set(
        key=access_token, value=dumps(access_token_data), expire=access_expires_at,
    )
    await redis_client.set(
        key=refresh_token, value=dumps(refresh_token_data), expire=refresh_expires_at,
    )

    tokens: Dict[str, Union[str, int]] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": access_expires_at,
    }

    return tokens


async def bearer_auth(
        request: Request,
        http_credentials: HTTPAuthorizationCredentials = Depends(
            HTTPBearer()
        ),  # pylint: disable=unused-argument
) -> Optional[str]:
    """Auth dependence, scope data set in TokenAuthMiddleware."""
    token_data: Dict[str, str] = request.scope.get("token_data", {})
    user_id: Optional[str] = token_data.get("user_id")

    return user_id


async def logout(access_token: Optional[str]) -> bool:
    """
    Wipe user's tokens
    :param access_token: user's access_token
    :return: bool result
    """
    if not access_token:
        return False

    raw_token_data = await redis_client.get(access_token)

    if not raw_token_data:
        return False

    token_data: Dict[str, Any] = loads(raw_token_data)
    refresh_token: Optional[str] = token_data.get("refresh_token")

    await redis_client.delete(access_token)

    if refresh_token:
        await redis_client.delete(refresh_token)

    return True


async def refresh_tokens(refresh_token: str) -> Dict[str, Union[str, int]]:
    """
    Recreate tokens pair
    :param refresh_token: current active refresh token
    :return: new tokens pair
    """
    raw_token_data: bytes = await redis_client.get(refresh_token)

    if not raw_token_data:
        raise UnauthorizedError

    token_data: Dict[str, Any] = loads(raw_token_data)
    access_token: str = token_data["access_token"]

    is_logout: bool = await logout(access_token=access_token)

    if not is_logout:
        raise UnauthorizedError

    tokens: Dict[str, Union[str, int]] = await create_tokens(
        user_id=token_data["user_id"]
    )

    return tokens


async def refresh_tokens_controller(request: Request) -> Dict[str, Union[str, int]]:
    """Controller for using as dependency in routes."""
    refresh_token: Optional[str] = request.scope.get("token")

    if not refresh_token:
        raise UnauthorizedError

    tokens: Dict[str, Union[str, int]] = await refresh_tokens(refresh_token)

    return tokens
