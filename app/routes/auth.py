"""Auth routes"""
from typing import Dict
from typing import Optional
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
from app.services.auth.base import refresh_tokens


async def process_auth_route(code: str) -> None:  # pylint: disable=unused-argument
    """Process test_auth test_routes"""
    ...


auth_router = APIRouter()  # pylint: disable-msg=C0103

fb_router = APIRouter(route_class=FacebookAuth)  # pylint: disable-msg=C0103
google_router = APIRouter(route_class=GoogleAuth)  # pylint: disable-msg=C0103
spotify_router = APIRouter(route_class=SpotifyAuth)  # pylint: disable-msg=C0103
vk_router = APIRouter(route_class=VKAuth)  # pylint: disable-msg=C0103

fb_router.add_api_route(
    path="/facebook/", methods=["POST"], endpoint=process_auth_route
)
google_router.add_api_route(
    path="/google/", methods=["POST"], endpoint=process_auth_route
)
spotify_router.add_api_route(
    path="/spotify/", methods=["POST"], endpoint=process_auth_route
)
vk_router.add_api_route(path="/vk/", methods=["POST"], endpoint=process_auth_route)

auth_router.include_router(fb_router)
auth_router.include_router(google_router)
auth_router.include_router(spotify_router)
auth_router.include_router(vk_router)


@auth_router.post("/logout/", response_model=LogoutOut, summary="Destroy test_auth session")
async def logout_route(
    request: Request, user_id: str = Depends(bearer_auth)  # pylint: disable=unused-argument
) -> LogoutOut:
    access_token: Optional[str] = request.scope.get("token")
    result: bool = await logout(access_token=access_token)
    response: LogoutOut = LogoutOut(data=result)

    return response


@auth_router.post("/refresh/", response_model=AuthOut, summary="Refresh tokens")
async def refresh_route(
    request: Request,
    user_id: str = Depends(bearer_auth)  # pylint: disable=unused-argument
) -> AuthOut:
    refresh_token: str = request.scope["token"]

    tokens: Dict[str, Union[str, int]] = await refresh_tokens(
        refresh_token=refresh_token
    )
    response: AuthOut = AuthOut(**tokens)  # type: ignore

    return response
