"""Setup FastAPI application"""

from fastapi import APIRouter
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.routes.auth import auth_router
from app.routes.challenges import challenges_router
from app.routes.playlists import playlists_router
from app.routes.submissions import submissions_router
from app.routes.tracks import tracks_router
from app.routes.users import router as users_route
from app.routes.utils import utils_router
from app.routes.votes import votes_router
from app.services.auth.middleware import TokenAuthMiddleware
from app.settings import TORTOISE_CONFIG
from app.utils.redis import register_redis


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
    register_redis(app)

    # Router section
    router = APIRouter()

    router.include_router(auth_router, prefix="/auth", tags=["Auth"])
    router.include_router(users_route, prefix="/users", tags=["Users"])
    router.include_router(playlists_router, prefix="/playlists", tags=["Playlists"])
    router.include_router(challenges_router, prefix="/challenges", tags=["Challenges"])
    router.include_router(tracks_router, prefix="/tracks", tags=["Tracks"])
    router.include_router(
        submissions_router, prefix="/submissions", tags=["Submissions"]
    )
    router.include_router(votes_router, prefix="/votes", tags=["Votes"])
    router.include_router(utils_router, prefix="/utils", tags=["Utils"])

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

    return app
