"""
VK OAuth integration
"""
from typing import Any
from typing import Dict
from typing import Tuple

from httpx import HTTPError
from httpx import Response

from app.extensions import http_client
from app.models.db.user import AuthProvider
from app.services.auth.base import OAuthRoute
from app.settings import VK_API_VERSION
from app.settings import VK_ID
from app.settings import VK_REDIRECT_URI
from app.settings import VK_SECRET
from app.utils.exceptions import UnauthorizedError


class VKAuth(OAuthRoute):
    """VK auth integration"""

    provider = AuthProvider.VK
    auth_endpoint = "https://oauth.vk.com/access_token"
    account_endpoint = "https://api.vk.com/method/users.get"

    async def code_auth(self, code: str) -> Tuple[str, str, int]:
        data: Dict[str, Any] = {
            "code": code,
            "client_id": VK_ID,
            "client_secret": VK_SECRET,
            "redirect_uri": VK_REDIRECT_URI,
            "v": VK_API_VERSION,
        }
        response: Response = await http_client.post(url=self.auth_endpoint, data=data)

        try:
            response.raise_for_status()
        except HTTPError:
            raise UnauthorizedError

        auth_data = response.json()
        access_token: str = auth_data["access_token"]
        refresh_token: str = ""
        expires: int = auth_data["expires_in"]

        return access_token, refresh_token, expires

    async def get_account_info(self, access_token: str) -> Dict[str, str]:
        params = {
            "fields": "uid,first_name,last_name,photo_400_orig",
            "access_token": access_token,
            "v": VK_API_VERSION,
        }
        response: Response = await http_client.get(
            url=self.account_endpoint, params=params
        )

        try:
            response.raise_for_status()
        except HTTPError:
            raise UnauthorizedError

        json_response = response.json()
        users = json_response.get("response", [])

        if not users and not isinstance(users, list):
            raise UnauthorizedError

        profile_info = users[0]
        user_id = profile_info.get("id")
        first_name = profile_info.get("first_name")
        last_name = profile_info.get("last_name")

        formatted_data = {
            "_id": str(user_id),
            "name": f"{first_name} {last_name}",
            "image": profile_info.get("photo_400_orig"),
            "url": f"https://vk.com/id{user_id}",
        }

        return formatted_data
