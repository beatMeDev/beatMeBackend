from app.settings.base import config


FACEBOOK_ID: str = config("FACEBOOK_ID", cast=str)
FACEBOOK_SECRET: str = config("FACEBOOK_SECRET", cast=str)
FACEBOOK_REDIRECT_URI: str = config("FACEBOOK_REDIRECT_URI", cast=str)
FACEBOOK_API_VERSION: str = config("FACEBOOK_API_VERSION", cast=str)

GOOGLE_ID: str = config("GOOGLE_ID", cast=str)
GOOGLE_SECRET: str = config("GOOGLE_SECRET", cast=str)
GOOGLE_REDIRECT_URI: str = config("GOOGLE_REDIRECT_URI", cast=str)

SPOTIFY_ID: str = config("SPOTIFY_ID", cast=str)
SPOTIFY_SECRET: str = config("SPOTIFY_SECRET", cast=str)
SPOTIFY_REDIRECT_URI: str = config("SPOTIFY_REDIRECT_URI", cast=str)

VK_ID: int = config("VK_ID", cast=int)
VK_SECRET: str = config("VK_SECRET", cast=str)
VK_REDIRECT_URI: str = config("VK_REDIRECT_URI", cast=str)
VK_API_VERSION: str = config("VK_API_VERSION", cast=str)

YOUTUBE_KEY: str = config("YOUTUBE_KEY", cast=str)
