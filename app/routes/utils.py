"""Utils endpoints"""
from random import randint
from typing import Optional

from fastapi import APIRouter
from tortoise.contrib.pydantic import PydanticModel

from app.models.api.utils import TextOut
from app.models.db import Text


utils_router = APIRouter()  # pylint: disable-msg=C0103


@utils_router.get("/text/random/", response_model=TextOut, summary="Loader text")
async def get_random_text_route() -> PydanticModel:
    """Get random text for loader."""
    texts_count: int = await Text.filter().count()
    offset: int = randint(0, texts_count - 1)
    text: Optional[Text] = await Text.filter().offset(offset).limit(1).first()

    response = await TextOut.from_tortoise_orm(text)

    return response
