import asyncio
import json
from asyncio import AbstractEventLoop
from datetime import datetime, timezone
from logging import Logger

import aioredis
from aioredis import Redis, exceptions

from app.settings import settings
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient
from app.usecases.schemas.unique_set import UniqueSetError, UniqueSetMessage


class RedisClient(IUniqueSetClient):
    """Redis client singleton."""

    def __init__(self, logger: Logger, loop: AbstractEventLoop) -> None:
        self.logger = logger
        self.redis = None
        self.message_cache = []
        loop.create_task(self.__manage_connection())
        loop.create_task(self.__process_message_cache())

    async def __connect(self) -> Redis:
        self.redis = await aioredis.from_url(settings.redis_url, encoding="utf-8")
        if await self.redis.ping():
            self.logger.info("[RedisClient]: Connection established.")

    async def __manage_connection(self) -> None:
        while True:
            try:
                if not self.redis:
                    await self.__connect()
                else:
                    await self.redis.ping()
            except (exceptions.ConnectionError, exceptions.RedisError) as e:
                self.logger.error("[RedisClient]: Connection error: %s", str(e))
                self.redis = None

            await asyncio.sleep(settings.redis_reconnect_frequency)

    async def __process_message_cache(self) -> None:
        while True:
            rescued_messages = []
            failed_rescues = []
            if self.message_cache and self.redis:
                for index, message in enumerate(self.message_cache):
                    try:
                        await self.publish(message=message)
                    except UniqueSetError:
                        failed_rescues.append(index)
                    else:
                        rescued_messages.append(index)

                for index in rescued_messages:
                    self.message_cache.pop(index)

                self.logger.info(
                    "[RedisClient]: Cached message results: %s succeeded, %s failed.",
                    len(rescued_messages),
                    len(failed_rescues),
                )

                rescued_messages, failed_rescues = [], []

            await asyncio.sleep(settings.redis_in_memory_cache_periodicity)

    async def publish(self, message: UniqueSetMessage) -> int:
        """Publishes message to unique set."""
        set_message = json.dumps(message.dict()).encode()
        current_date = datetime.now(timezone.utc)
        current_time = current_date.timestamp()
        try:
            result = await self.redis.zadd(
                settings.redis_zset, {set_message: current_time}
            )
            self.logger.info("[RedisClient]: Message published:\n%s", message)
            return result
        except exceptions.ConnectionError as e:
            self.logger.error(
                "[RedisClient]: Message not published due to connection error, attempting reconnect..."
            )
            self.message_cache.append(message)
            raise UniqueSetError(detail=str(e)) from e
        except exceptions.RedisError as e:
            self.logger.error(
                "[RedisClient]: Message not published.\nError: %s", str(e)
            )
            self.message_cache.append(message)
            raise UniqueSetError(detail=str(e)) from e

    async def close_connection(self) -> None:
        """Closes external connection."""
        if self.redis:
            self.redis.close()
            self.redis = None
            self.logger.info("[RedisClient]: Connection closed.")
