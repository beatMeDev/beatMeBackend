"""Test pre running stuff"""
import warnings

from typing import AsyncGenerator
from uuid import uuid4

import pytest

from asyncpg import ObjectInUseError
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError

from app.models.db import AuthAccount
from app.models.db import Playlist
from app.models.db import Text
from app.models.db import Track
from app.models.db import User
from app.models.db.user import AuthProvider
from app.settings import APP_MODELS
from app.settings import TORTOISE_TEST_DB
from tests.test_services.test_auth.test_base import USER_UUID


with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import imp  # pylint: disable=unused-import


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.asyncio
async def test_db() -> AsyncGenerator:  # type: ignore
    """Initialize db connection before run test."""
    try:
        await Tortoise.init(db_url=TORTOISE_TEST_DB, modules={"models": APP_MODELS})
    except DBConnectionError:
        await Tortoise.init(
            db_url=TORTOISE_TEST_DB, modules={"models": APP_MODELS}, _create_db=True,
        )
    await Tortoise.generate_schemas()

    yield

    try:
        await Tortoise._drop_databases()  # pylint: disable=protected-access
    except ObjectInUseError:
        pass

    await Tortoise.close_connections()


POPULATE_TRACK_ID: str = str(uuid4())


@pytest.fixture()
@pytest.mark.asyncio
async def populate_texts() -> None:
    """Populate text for utils routes tests."""
    await Text.create(content="test")


@pytest.fixture()
@pytest.mark.asyncio
async def populate_track() -> Track:
    """Populate track for utils routes tests."""
    track, _ = await Track.get_or_create(
        id=POPULATE_TRACK_ID,
        name="test",
        author_name="test",
        cover_url="test",
        preview_url="test",
        youtube_id="test",
        spotify_id="test",
        recommended=True,
        meta={},
    )

    return track


@pytest.fixture()
@pytest.mark.asyncio
async def populate_playlist_with_track() -> None:
    """Populate playlist with track for routes testing."""
    playlist, _ = await Playlist.get_or_create(
        name="test",
        url="test",
        spotify_id="test",
        recommended=True,
    )
    track, _ = await Track.get_or_create(
        id=POPULATE_TRACK_ID,
        name="test",
        author_name="test",
        cover_url="test",
        preview_url="test",
        youtube_id="test",
        spotify_id="test",
        recommended=True,
        meta={},
    )
    await playlist.tracks.add(track)


@pytest.fixture()
@pytest.mark.asyncio
async def populate_user() -> None:
    """Populate user for routes testing."""
    user: User = await User.create(id=USER_UUID)
    auth_account: AuthAccount = await AuthAccount.create(
        _id="test",
        name="test",
        image="test",
        url="test",
        provider=AuthProvider.DEFAULT,
        access_token="test",
        refresh_token="test",
        expires=0,
    )
    await user.auth_accounts.add(auth_account)
