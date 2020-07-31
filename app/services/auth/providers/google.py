"""
Google OAuth integration
"""
from datetime import datetime
from typing import Dict
from typing import Tuple

from httpx import HTTPError
from httpx import Response

from app.extensions import http_client
from app.models.db.user import AuthProvider
from app.services.auth.base import OAuthRoute
from app.settings import GOOGLE_ID
from app.settings import GOOGLE_REDIRECT_URI
from app.settings import GOOGLE_SECRET
from app.utils.exceptions import UnauthorizedError


class GoogleAuth(OAuthRoute):
    """Google auth integration"""

    provider = AuthProvider.GOOGLE
    auth_endpoint = "https://oauth2.googleapis.com/token"
    account_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"

    async def code_auth(self, code: str) -> Tuple[str, str, int]:
        data: Dict[str, str] = {
            "code": code,
            "client_id": GOOGLE_ID,
            "client_secret": GOOGLE_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        response: Response = await http_client.post(url=self.auth_endpoint, data=data)

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
        params = {"access_token": access_token}
        response = await http_client.get(
            url=self.account_endpoint, params=params, headers=headers
        )

        try:
            response.raise_for_status()
        except HTTPError:
            raise UnauthorizedError

        profile_info = response.json()

        formatted_data = {
            "_id": str(profile_info.get("sub")),
            "name": profile_info.get("name"),
            "image": profile_info.get("picture"),
            "url": profile_info.get("link"),
        }

        return formatted_data
