"""External services settings"""
from app.settings.base import config


FACEBOOK_ID: str = config("FACEBOOK_ID", cast=str, default="")
FACEBOOK_SECRET: str = config("FACEBOOK_SECRET", cast=str, default="")
FACEBOOK_REDIRECT_URI: str = config("FACEBOOK_REDIRECT_URI", cast=str, default="")
FACEBOOK_API_VERSION: str = config("FACEBOOK_API_VERSION", cast=str, default="")
FACEBOOK_SCOPE: str = config(
    "FACEBOOK_SCOPE", cast=str, default="user_link,public_profile",
)

GOOGLE_ID: str = config("GOOGLE_ID", cast=str, default="")
GOOGLE_SECRET: str = config("GOOGLE_SECRET", cast=str, default="")
GOOGLE_REDIRECT_URI: str = config("GOOGLE_REDIRECT_URI", cast=str, default="")
GOOGLE_SCOPE: str = config(
    "GOOGLE_SCOPE", cast=str, default="openid email profile",
)

SPOTIFY_ID: str = config("SPOTIFY_ID", cast=str, default="")
SPOTIFY_SECRET: str = config("SPOTIFY_SECRET", cast=str, default="")
SPOTIFY_REDIRECT_URI: str = config("SPOTIFY_REDIRECT_URI", cast=str, default="")
SPOTIFY_API: str = config(
    "SPOTIFY_API", cast=str, default="https://api.spotify.com/v1/"
)
SPOTIFY_SCOPE: str = config(
    "SPOTIFY_SCOPE", cast=str, default="user-read-private,user-read-email",
)

VK_ID: int = config("VK_ID", cast=int, default=0)
VK_SECRET: str = config("VK_SECRET", cast=str, default="")
VK_REDIRECT_URI: str = config("VK_REDIRECT_URI", cast=str, default="")
VK_API_VERSION: str = config("VK_API_VERSION", cast=str, default="")
VK_SCOPE: str = config(
    "VK_SCOPE", cast=str, default="offline,friends,email",
)

YOUTUBE_KEY: str = config("YOUTUBE_KEY", cast=str, default="")
