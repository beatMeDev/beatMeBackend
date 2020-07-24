"""App extensions"""
from aioredis import Redis
from httpx import AsyncClient


http_client = AsyncClient()  # pylint: disable-msg=C0103
redis_client = Redis(pool_or_conn=None)  # pylint: disable-msg=C0103
