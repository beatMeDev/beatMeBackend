"""External services settings"""
from app.settings.base import config


FACEBOOK_ID: str = config("FACEBOOK_ID", cast=str, default="")
FACEBOOK_SECRET: str = config("FACEBOOK_SECRET", cast=str, default="")
FACEBOOK_REDIRECT_URI: str = config("FACEBOOK_REDIRECT_URI", cast=str, default="")
FACEBOOK_API_VERSION: str = config("FACEBOOK_API_VERSION", cast=str, default="")

GOOGLE_ID: str = config("GOOGLE_ID", cast=str, default="")
GOOGLE_SECRET: str = config("GOOGLE_SECRET", cast=str, default="")
GOOGLE_REDIRECT_URI: str = config("GOOGLE_REDIRECT_URI", cast=str, default="")

SPOTIFY_ID: str = config("SPOTIFY_ID", cast=str, default="")
SPOTIFY_SECRET: str = config("SPOTIFY_SECRET", cast=str, default="")
SPOTIFY_REDIRECT_URI: str = config("SPOTIFY_REDIRECT_URI", cast=str, default="")
SPOTIFY_API: str = config("SPOTIFY_API", cast=str, default="https://api.spotify.com/v1/")

VK_ID: int = config("VK_ID", cast=int, default=0)
VK_SECRET: str = config("VK_SECRET", cast=str, default="")
VK_REDIRECT_URI: str = config("VK_REDIRECT_URI", cast=str, default="")
VK_API_VERSION: str = config("VK_API_VERSION", cast=str, default="")

YOUTUBE_KEY: str = config("YOUTUBE_KEY", cast=str, default="")
