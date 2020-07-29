"""Setup FastAPI application"""
import sys
import warnings

from typing import Dict
from typing import Union

import aioredis

from fastapi import APIRouter
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.extensions import redis_client
from app.routes.auth import auth_router
from app.routes.challenges import challenges_router
from app.routes.playlists import playlists_router
from app.routes.tracks import tracks_router
from app.routes.users import router as users_route
from app.services.auth.middleware import TokenAuthMiddleware
from app.settings import REDIS_DB
from app.settings import REDIS_HOST
from app.settings import REDIS_PASSWORD
from app.settings import REDIS_PORT
from app.settings import TORTOISE_CONFIG


def get_application() -> FastAPI:
    """
    Generate application
    """
    app: FastAPI = FastAPI(title="Beat Me", docs_url="/swagger/")

    # Init extensions sections
    register_tortoise(
        app,
        config=TORTOISE_CONFIG,
        # modules={"models": ["db.user", "db.playlist"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )

    # Router section
    router = APIRouter()

    router.include_router(auth_router, prefix="/auth", tags=["Auth"])
    router.include_router(users_route, prefix="/users", tags=["Users"])
    router.include_router(playlists_router, prefix="/playlists", tags=["Playlists"])
    router.include_router(challenges_router, prefix="/challenges", tags=["Challenges"])
    router.include_router(tracks_router, prefix="/tracks", tags=["Tracks"])
    app.include_router(router, prefix="/api")

    # Middleware section
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TokenAuthMiddleware)

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

    return app


application = get_application()
