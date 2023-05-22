import asyncio
import json
from asyncio import AbstractEventLoop
from datetime import datetime, timezone
from logging import Logger
from typing import List, Optional

import aioredis
from aioredis import Redis, exceptions

from app.settings import settings
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.schemas.relays import CacheStatus, Status, UpdateRepoAdapter
from app.usecases.schemas.unique_set import UniqueSetError, UniqueSetMessage


class RedisClient(IUniqueSetClient):
    """Redis client singleton."""

    def __init__(
        self, logger: Logger, loop: AbstractEventLoop, relays_repo: IRelaysRepo
    ) -> None:
        self.logger = logger
        self.relays_repo = relays_repo
        self.redis: Optional[Redis] = None
        self.message_cache: List[UniqueSetMessage] = []
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
                for message in self.message_cache:
                    try:
                        await self.publish(message=message)
                    except UniqueSetError:
                        failed_rescues.append(message)
                    else:
                        rescued_messages.append(message)

                        await self.relays_repo.update(
                            relay=UpdateRepoAdapter(
                                emitter_address=message.emitter_address,
                                source_chain_id=message.emitter_chain,
                                sequence=message.sequence,
                                status=Status.PENDING,
                                error=None,
                                cache_status=CacheStatus.PREVIOUSLY_CACHED,
                            )
                        )

                for message in rescued_messages:
                    self.message_cache = [m for m in self.message_cache if m != message]

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
        if self.redis:
            try:
                result = await self.redis.zadd(
                    settings.redis_zset, {set_message: current_time}
                )
                self.logger.info(
                    "[RedisClient]: Message published; emitter chain: %s, sequence: %s",
                    message.emitter_chain,
                    message.sequence,
                )
                return result
            except exceptions.ConnectionError as e:
                self.logger.error(
                    "[RedisClient]: Connection error; message not published; attempting reconnect..."
                )
                self.message_cache.append(message)
                raise UniqueSetError(detail=str(e)) from e
            except exceptions.RedisError as e:
                self.logger.error(
                    "[RedisClient]: Unexpected error; message not published.\n\nError: %s",
                    str(e),
                )
                self.message_cache.append(message)
                raise UniqueSetError(detail=str(e)) from e
        else:
            self.message_cache.append(message)
            self.logger.error(
                "[RedisClient]: Message cached; emitter chain: %s, sequence: %s",
                message.emitter_chain,
                message.sequence,
            )
            raise UniqueSetError(detail="Redis is not connected.")

    async def close_connection(self) -> None:
        """Closes external connection."""
        if self.redis:
            await self.redis.close()
            self.redis = None
            self.logger.info("[RedisClient]: Connection closed.")
