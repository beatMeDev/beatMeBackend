"""Init redis connection when app starts."""
import sys
import warnings

from typing import Dict
from typing import Union

import aioredis

from fastapi import FastAPI

from app.extensions import redis_client
from app.settings import REDIS_DB
from app.settings import REDIS_HOST
from app.settings import REDIS_PASSWORD
from app.settings import REDIS_PORT


def register_redis(app: FastAPI) -> None:
    """Add redis logic for app events."""
    @app.on_event("startup")
    async def startup() -> None:  # pylint: disable=unused-variable
        """On startup app init redis connection"""
        redis_kwargs: Dict[str, Union[str, int]] = {
            "address": f"redis://{REDIS_HOST}:{REDIS_PORT}",
            "db": REDIS_DB,
            "password": REDIS_PASSWORD,
        }
        redis_kwargs = {key: value for key, value in redis_kwargs.items() if value}

        try:
            redis_pool: aioredis.ConnectionsPool = await aioredis.create_redis_pool(
                **redis_kwargs
            )
        except ConnectionRefusedError:
            warnings.warn("REDIS error, check connection settings")
            sys.exit()

        redis_client.__init__(redis_pool)

    @app.on_event("shutdown")
    async def shutdown() -> None:  # pylint: disable=unused-variable
        """On shutdown app close redis connection"""
        redis_client.close()
