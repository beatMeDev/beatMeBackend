"""Base database utils"""
from asyncio import gather
from typing import List
from typing import Tuple
from typing import Type

from fastapi import Query
from tortoise import QuerySet
from tortoise.contrib.pydantic import PydanticListModel
from tortoise.contrib.pydantic import PydanticModel
from tortoise.models import MODEL

from app.settings import PAGE_LIMIT
from app.settings import PAGE_MAX_LIMIT


class Paginate:  # pylint: disable=too-few-public-methods
    """Pagination dependency."""
    def __init__(
            self,
            limit: int = Query(default=PAGE_LIMIT, le=PAGE_MAX_LIMIT),
            offset: int = Query(default=0, ge=0)
    ):
        self.limit: int = limit
        self.offset: int = offset

    async def paginate(
            self,
            queryset: QuerySet[MODEL],
            serializer: Type[PydanticListModel],
    ) -> Tuple[int, List[PydanticModel]]:
        """
        Paginate query
        :param queryset: Tortoise queryset
        :param serializer: Tortoise pydantic serializer
        :param offset: offset
        :param limit: limit
        :return: query count, filter counts
        """
        count, items = await gather(
            queryset.count(),
            serializer.from_queryset(queryset.limit(self.limit).offset(self.offset))
        )

        return count, items.__root__
