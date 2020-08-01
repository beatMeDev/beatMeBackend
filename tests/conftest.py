"""Test pre running stuff"""
import warnings

from typing import AsyncGenerator
from uuid import uuid4

import pytest

from asyncpg import ObjectInUseError
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError

from app.models.db import Text
from app.models.db import Track
from app.settings import APP_MODELS
from app.settings import TORTOISE_TEST_DB


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
async def populate_track() -> None:
    """Populate track for utils routes tests."""
    await Track.create(
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
