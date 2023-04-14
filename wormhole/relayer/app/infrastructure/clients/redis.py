import asyncio
from asyncio import AbstractEventLoop
from datetime import datetime, timezone
from logging import Logger

import aioredis
from aioredis import Redis, exceptions

from app.settings import settings
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery


class RedisClient(IUniqueSetClient):
    def __init__(
        self, vaa_delivery: IVaaDelivery, logger: Logger, loop: AbstractEventLoop
    ) -> None:
        self.vaa_delivery = vaa_delivery
        self.script = """
        local items = redis.call("zrangebyscore", KEYS[1], "-inf", ARGV[1])
        if #items > 0 then
            redis.call("zrem", KEYS[1], unpack(items))
        end
        return items
        """
        self.logger = logger
        loop.create_task(self.__start_consumption())

    async def __connect(self) -> Redis:
        """Connect to Redis."""
        redis = await aioredis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )
        if await redis.ping():
            self.logger.info("[RedisClient]: Established connection.")
        return redis

    async def __start_consumption(self) -> None:
        """Starts listening for messages to consume."""
        while True:
            try:
                redis = await self.__connect()
                script_sha = await redis.script_load(self.script)

                while True:
                    await asyncio.sleep(settings.redis_consumption_frequency)
                    current_date = datetime.now(timezone.utc)
                    current_time = current_date.timestamp()
                    max_score = current_time - settings.redis_min_message_age

                    messages = await redis.evalsha(
                        script_sha, 1, settings.redis_zset, max_score
                    )
                    for message in messages:
                        await self.__on_message(message=message)
            except exceptions.ConnectionError:
                self.logger.error(
                    "[RedisClient]: Connection error, attempting reconnect..."
                )
                await asyncio.sleep(settings.redis_reconnect_frequency)

            except exceptions.RedisError as e:
                self.logger.error("[RedisClient]: Unexpected error: %s", str(e))

    async def __on_message(self, message: bytes) -> None:
        """Handle receiving an individual Redis message."""

        self.logger.info("[RedisClient]: Received message: %s.", str(message))

        await self.vaa_delivery.process(message=message)
