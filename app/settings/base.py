"""Base settings"""
from pathlib import PurePath

from decouple import AutoConfig


APP_ROOT_FOLDER = PurePath(__file__).parent.parent

config = AutoConfig(search_path=APP_ROOT_FOLDER)

# Database section
POSTGRES_USER: str = config("DATABASE_USER", cast=str, default="postgres")
POSTGRES_PASSWORD: str = config("DATABASE_PASSWORD", cast=str, default="postgres")
POSTGRES_HOST: str = config("DATABASE_HOST", cast=str, default="127.0.0.1")
POSTGRES_PORT: str = config("DATABASE_PORT", cast=str, default="5432")
POSTGRES_NAME: str = config("DATABASE_NAME", cast=str, default="postgres")

APP_MODELS = [
    "app.models.db",
]
TORTOISE_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": POSTGRES_HOST,
                "port": POSTGRES_PORT,
                "user": POSTGRES_USER,
                "password": POSTGRES_PASSWORD,
                "database": POSTGRES_NAME,
                "maxsize": 10,
            },
        },
    },
    "apps": {"models": {"models": APP_MODELS, "default_connection": "default"}},
}
TORTOISE_TEST_DB = "sqlite://:memory:"
# TORTOISE_TEST_CONFIG = {
#     "connections": {
#         "default": {
#             "engine": "tortoise.backends.asyncpg",
#             "credentials": {
#                 "host": POSTGRES_HOST,
#                 "port": POSTGRES_PORT,
#                 "user": POSTGRES_USER,
#                 "password": POSTGRES_PASSWORD,
#                 "database": "test_{}",
#                 "maxsize": 10,
#             },
#         },
#     },
#     "apps": {
#         "models": {"models": APP_MODELS, "default_connection": "default", },
#     },
# }

# Redis section
REDIS_HOST: str = config("REDIS_HOST", cast=str, default="127.0.0.1")
REDIS_PORT: int = config("REDIS_PORT", cast=int, default=6379)
REDIS_DB: int = config("REDIS_DB", cast=int, default=0)
REDIS_PASSWORD: str = config("REDIS_PASSWORD", cast=str, default="")

# Auth section
JWT_SECRET: str = config("JWT_SECRET", cast=str, default="dev")
ITEM_SECRET: str = config("ITEM_SECRET", cast=str, default="dev")
JWT_ALGORITHM: str = config("JWT_ALGORITHM", cast=str, default="HS256")
ACCESS_TOKEN_LIFETIME: int = config(
    "ACCESS_TOKEN_LIFETIME", cast=int, default=7 * 24 * 60 * 60
)
REFRESH_TOKEN_LIFETIME: int = config(
    "REFRESH_TOKEN_LIFETIME", cast=int, default=30 * 24 * 60 * 60
)

# Pagination section
PAGE_LIMIT = config("PAGE_LIMIT", cast=int, default=10)
PAGE_MAX_LIMIT = config("PAGE_MAX_LIMIT", cast=int, default=20)
