"""
Base auth services
"""
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
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
from app.utils.exceptions import UnauthorizedError


class OAuthRoute(APIRoute):
    """
    Base OAuth fastapi route class.

    get_route_handler - main test_auth logic,
    code_auth and get_account_info should be implemented in third party providers.
    """

    provider = AuthProvider.DEFAULT
    auth_endpoint: str = ""
    account_endpoint: str = ""

    async def code_auth(self, code: str) -> str:
        """
        Exchange code to access token
        :param code: authorization code
        :return: access token
        """
        raise NotImplementedError

    async def get_account_info(self, access_token: str) -> Dict[str, str]:
        """
        Get profile information
        :param access_token: test_auth service token
        :return: profile information: {"id": "1", "name": "Test", "image": "link", "url": "link"}
        """
        raise NotImplementedError

    def get_route_handler(self) -> Callable:  # type: ignore
        original_route_handler: Callable = super().get_route_handler()  # type: ignore

        async def custom_route_handler(request: Request) -> Response:
            await original_route_handler(request)

            user_id: Optional[str] = request.scope.get("user_id")
            code: str = request.query_params.get("code")
            access_token: str = await self.code_auth(code=code)
            account_info: Dict[str, str] = await self.get_account_info(
                access_token=access_token
            )
            account_info["provider"] = self.provider
            account_info["access_token"] = access_token
            account_created: bool = False
            user_created: bool = False
            auth_account: AuthAccount = await AuthAccount.filter(
                id=account_info["id"]
            ).first()

            if auth_account:
                await auth_account.update_from_dict(data=account_info)
                await auth_account.save()
            else:
                auth_account = await AuthAccount.create(**account_info)
                account_created = True

            if user_id and account_created:
                user: User = await User.get(id=user_id)
            elif not user_id and not account_created:
                user = await User.filter(auth_accounts__in=[auth_account]).first()
            else:
                user = await User.create()
                user_created = True

            if account_created or user_created:
                await user.auth_accounts.add(auth_account)

            tokens: Dict[str, Union[str, int]] = await create_tokens(
                user_id=str(user.id)
            )

            return ORJSONResponse(tokens)

        return custom_route_handler


async def create_tokens(user_id: str) -> Dict[str, Union[str, int]]:
    """
    Create test_auth tokens
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
    http_credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),  # pylint: disable=unused-argument
) -> Optional[str]:
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
