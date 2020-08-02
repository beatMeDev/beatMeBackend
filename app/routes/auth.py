"""Auth routes"""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request

from app.models.api.auth import AuthOut
from app.models.api.auth import LogoutOut
from app.services.auth import FacebookAuth
from app.services.auth import GoogleAuth
from app.services.auth import SpotifyAuth
from app.services.auth import VKAuth
from app.services.auth.base import bearer_auth
from app.services.auth.base import logout
from app.services.auth.base import refresh_tokens_controller


async def process_auth_route(code: Optional[str] = None) -> None:  # pylint: disable=unused-argument
    """Process auth routes"""
    ...


auth_router = APIRouter()  # pylint: disable-msg=C0103

providers: List[Tuple[Any, str]] = [
    (FacebookAuth, "/facebook/", ),
    (GoogleAuth, "/google/", ),
    (SpotifyAuth, "/spotify/", ),
    (VKAuth, "/vk/", ),
]

for provider, endpoint in providers:
    router = APIRouter(route_class=provider)
    router.add_api_route(
        path=endpoint, methods=["GET", "POST"], endpoint=process_auth_route
    )
    auth_router.include_router(router)


@auth_router.post("/logout/", response_model=LogoutOut, summary="Destroy auth session")
async def logout_route(
        request: Request,
        user_id: str = Depends(bearer_auth),  # pylint: disable=unused-argument
) -> LogoutOut:
    """Logout user endpoint."""
    access_token: Optional[str] = request.scope.get("token")
    result: bool = await logout(access_token=access_token)
    response: LogoutOut = LogoutOut(data=result)

    return response


@auth_router.post("/refresh/", response_model=AuthOut, summary="Refresh tokens")
async def refresh_route(
        user_id: str = Depends(bearer_auth),  # pylint: disable=unused-argument
        tokens: Dict[str, Union[str, int]] = Depends(refresh_tokens_controller)
) -> AuthOut:
    """Refresh user tokens endpoint."""
    response: AuthOut = AuthOut(**tokens)  # type: ignore

    return response
