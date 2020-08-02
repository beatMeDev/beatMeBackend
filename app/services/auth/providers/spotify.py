"""
Spotify OAuth integration
"""
from base64 import b64encode
from datetime import datetime
from typing import Dict
from typing import Optional
from typing import Tuple
from urllib.parse import urlencode

from fastapi import Depends
from httpx import HTTPError
from httpx import Response

from app.extensions import http_client
from app.models.db.user import AuthAccount
from app.models.db.user import AuthProvider
from app.services.auth.base import OAuthRoute
from app.services.auth.base import bearer_auth
from app.settings import SPOTIFY_ID
from app.settings import SPOTIFY_REDIRECT_URI
from app.settings import SPOTIFY_SCOPE
from app.settings import SPOTIFY_SECRET
from app.utils.exceptions import UnauthorizedError


class SpotifyAuth(OAuthRoute):
    """Spotify auth integration"""

    provider = AuthProvider.SPOTIFY
    auth_endpoint = "https://accounts.spotify.com/api/token"
    account_endpoint = "https://api.spotify.com/v1/me/"
    sign_in_endpoint = "https://accounts.spotify.com/authorize"

    async def code_auth(self, code: str) -> Tuple[str, str, int]:
        authorization = b64encode(
            f"{SPOTIFY_ID}:{SPOTIFY_SECRET}".encode("utf-8")
        ).decode("utf-8")
        headers: Dict[str, str] = {"Authorization": f"Basic {authorization}"}
        data: Dict[str, str] = {
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "code": code,
            "grant_type": "authorization_code",
        }

        response: Response = await http_client.post(
            url=self.auth_endpoint, data=data, headers=headers
        )

        try:
            response.raise_for_status()
        except HTTPError:
            raise UnauthorizedError

        auth_data = response.json()
        now_seconds = int(datetime.utcnow().timestamp())
        access_token: str = auth_data["access_token"]
        refresh_token: str = auth_data["refresh_token"]
        expires: int = now_seconds + int(auth_data["expires_in"])

        return access_token, refresh_token, expires

    async def get_account_info(self, access_token: str) -> Dict[str, str]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await http_client.get(url=self.account_endpoint, headers=headers)

        try:
            response.raise_for_status()
        except HTTPError:
            raise UnauthorizedError

        profile_info = response.json()

        profile_image: str = profile_info["images"][-1]["url"] if profile_info.get(
            "images"
        ) else ""
        formatted_data = {
            "_id": str(profile_info.get("id")),
            "name": profile_info.get("display_name"),
            "image": profile_image,
            "url": profile_info.get("external_urls", {}).get("spotify"),
        }

        return formatted_data

    async def create_auth_link(self) -> str:
        params: Dict[str, str] = {
            "response_type": "code",
            "client_id": SPOTIFY_ID,
            "scope": SPOTIFY_SCOPE,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
        }
        query: str = urlencode(params)
        url: str = f"{self.sign_in_endpoint}?{query}"

        return url


async def spotify_auth(
        user_id: Optional[str] = Depends(bearer_auth),
) -> str:
    """Spotify auth dependence"""
    if not user_id:
        raise UnauthorizedError

    auth_account: Optional[AuthAccount] = await AuthAccount.filter(
        user_id=user_id, provider=AuthProvider.SPOTIFY
    ).first()

    if not auth_account:
        raise UnauthorizedError

    now_seconds = int(datetime.utcnow().timestamp())

    if auth_account.expires < now_seconds:
        access_token, refresh_token, expires = await refresh_spotify_token(
            refresh_token=auth_account.refresh_token
        )
        auth_account.access_token = access_token  # type: ignore
        auth_account.refresh_token = refresh_token  # type: ignore
        auth_account.expires = expires  # type: ignore
        await auth_account.save()

    return auth_account.access_token


async def refresh_spotify_token(refresh_token: str) -> Tuple[str, str, int]:
    """
    Exchange refresh token to new access token
    :param refresh_token: spotify user's refresh token
    :return: access token, refresh token, when token expires in timestamp
    """
    refresh_url: str = "https://accounts.spotify.com/api/token"
    data: Dict[str, str] = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    authorization = b64encode(f"{SPOTIFY_ID}:{SPOTIFY_SECRET}".encode("utf-8")).decode(
        "utf-8"
    )
    headers: Dict[str, str] = {"Authorization": f"Basic {authorization}"}

    response: Response = await http_client.post(
        url=refresh_url, data=data, headers=headers
    )

    try:
        response.raise_for_status()
    except HTTPError:
        raise UnauthorizedError

    response_data = response.json()
    now_seconds = int(datetime.utcnow().timestamp())
    access_token: str = response_data["access_token"]
    expires: int = now_seconds + int(response_data["expires_in"])

    return access_token, refresh_token, expires
