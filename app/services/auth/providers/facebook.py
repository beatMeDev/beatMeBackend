"""
Facebook OAuth integration
"""
from typing import Dict

from httpx import HTTPError

from app.extensions import http_client
from app.models.db.user import AuthProvider
from app.services.auth.base import OAuthRoute
from app.settings import FACEBOOK_API_VERSION
from app.settings import FACEBOOK_ID
from app.settings import FACEBOOK_REDIRECT_URI
from app.settings import FACEBOOK_SECRET
from app.utils.exceptions import UnauthorizedError


class FacebookAuth(OAuthRoute):
    """Facebook auth integration"""
    provider = AuthProvider.FACEBOOK
    auth_endpoint = (
        f"https://graph.facebook.com/{FACEBOOK_API_VERSION}/oauth/access_token"
    )
    account_endpoint = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}/me/"

    async def code_auth(self, code: str) -> str:
        params = {
            "code": code,
            "redirect_uri": FACEBOOK_REDIRECT_URI,
            "client_secret": FACEBOOK_SECRET,
            "client_id": FACEBOOK_ID,
        }
        response = await http_client.get(url=self.auth_endpoint, params=params)

        try:
            response.raise_for_status()
        except HTTPError:
            raise UnauthorizedError

        auth_data = response.json()
        access_token: str = auth_data["access_token"]

        return access_token

    async def get_account_info(self, access_token: str) -> Dict[str, str]:
        params = {
            "access_token": access_token,
            "fields": "id,link,last_name,first_name,picture",
        }
        response = await http_client.get(url=self.account_endpoint, params=params)

        try:
            response.raise_for_status()
        except HTTPError:
            raise UnauthorizedError

        profile_info = response.json()
        first_name = profile_info.get("first_name")
        last_name = profile_info.get("last_name")

        formatted_data = {
            "id": str(profile_info.get("id")),
            "name": f"{first_name} {last_name}",
            "image": profile_info.get("picture", {}).get("data", {}).get("url"),
            "url": profile_info.get("link"),
        }

        return formatted_data
