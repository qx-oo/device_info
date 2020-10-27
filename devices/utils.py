import aioredis
from django.conf import settings


async def get_conn():
    client = await aioredis.create_redis_pool(
        settings.REDIS_URL, db=7)
    return client


class RedisClient():
    """
    get redis client
    example:
        with RedisClient() as client:
            client.set("test", "test val")
    """

    async def __aenter__(self):
        self.conn = await get_conn()
        return self.conn

    async def __aexit__(self, type, value, traceback):
        self.conn.close()
        await self.conn.wait_closed()
        return False
