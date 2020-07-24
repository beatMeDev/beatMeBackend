"""
Spotify OAuth integration
"""
from base64 import b64encode
from typing import Dict

from httpx import HTTPError

from app.extensions import http_client
from app.models.db.user import AuthProvider
from app.services.auth.base import OAuthRoute
from app.settings import SPOTIFY_ID
from app.settings import SPOTIFY_REDIRECT_URI
from app.settings import SPOTIFY_SECRET
from app.utils.exceptions import UnauthorizedError


class SpotifyAuth(OAuthRoute):
    """Spotify auth integration"""
    provider = AuthProvider.SPOTIFY
    auth_endpoint = "https://accounts.spotify.com/api/token"
    account_endpoint = "https://api.spotify.com/v1/me/"

    async def code_auth(self, code: str) -> str:
        auth_token = b64encode(f"{SPOTIFY_ID}:{SPOTIFY_SECRET}".encode("utf-8")).decode(
            "utf-8"
        )
        headers = {"Authorization": f"Basic {auth_token}"}
        data = {
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "code": code,
            "grant_type": "authorization_code",
        }

        response = await http_client.post(
            url=self.auth_endpoint, data=data, headers=headers
        )

        try:
            response.raise_for_status()
        except HTTPError:
            raise UnauthorizedError

        auth_data = response.json()
        access_token: str = auth_data["access_token"]

        return access_token

    async def get_account_info(self, access_token: str) -> Dict[str, str]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await http_client.get(url=self.account_endpoint, headers=headers)

        try:
            response.raise_for_status()
        except HTTPError:
            raise UnauthorizedError

        profile_info = response.json()

        formatted_data = {
            "id": str(profile_info.get("id")),
            "name": profile_info.get("display_name"),
            "image": profile_info.get("images", [])[-1].get("url")
            if profile_info.get("images", [])
            else "",
            "url": profile_info.get("external_urls", {}).get("spotify"),
        }

        return formatted_data
