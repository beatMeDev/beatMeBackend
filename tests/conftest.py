from typing import AsyncGenerator

import pytest

from asyncpg import ObjectInUseError
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError

from app.settings import APP_MODELS
from app.settings import TORTOISE_TEST_DB


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.asyncio
async def db() -> AsyncGenerator:  # type: ignore
    try:
        await Tortoise.init(db_url=TORTOISE_TEST_DB, modules={"models": APP_MODELS})
    except DBConnectionError:
        await Tortoise.init(
            db_url=TORTOISE_TEST_DB, modules={"models": APP_MODELS}, _create_db=True,
        )
    await Tortoise.generate_schemas()

    yield

    try:
        await Tortoise._drop_databases()
    except ObjectInUseError:
        pass

    await Tortoise.close_connections()
