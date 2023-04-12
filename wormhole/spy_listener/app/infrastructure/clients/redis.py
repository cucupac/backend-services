import asyncio
import json
from datetime import datetime, timezone
from logging import Logger

from redis import Redis, exceptions

from app.settings import settings
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient
from app.usecases.schemas.unique_set import UniqueSetError, UniqueSetMessage

# TODO: on reconnect, need some way to retreive in-memory messages


class RedisClient(IUniqueSetClient):
    """Redis client singleton."""

    def __init__(self, logger: Logger) -> None:
        self.connection = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
        )
        self.logger = logger
        self.reconnecting = False

    async def __reconnect(self):
        self.reconnecting = True
        while True:
            try:
                self.connection = Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password,
                )
                self.connection.ping()
            except exceptions.ConnectionError:
                self.logger.info(
                    "[RedisClient]: Connection error, attempting reconnect..."
                )
                await asyncio.sleep(settings.redis_reconnect_frequency)
            else:
                self.reconnecting = False
                self.logger.info("[RedisClient]: Reconnection successful.")
                return

    async def publish(self, message: UniqueSetMessage) -> None:
        """Publishes message to unique set."""
        set_message = json.dumps(message.dict()).encode()
        current_date = datetime.now(timezone.utc)
        current_time = current_date.timestamp()
        try:
            self.connection.zadd(settings.redis_zset, {set_message: current_time})
        except exceptions.ConnectionError as e:
            self.logger.error(
                "[RedisClient]: Connection error, attempting reconnect..."
            )
            # TODO: add message to in-memory set (but do this somewhere else...?)
            if not self.reconnecting:
                await self.__reconnect()
            raise UniqueSetError(detail=str(e)) from e
        except exceptions.RedisError as e:
            self.logger.error(
                "[RedisClient]: Message not published.\nError: %s", str(e)
            )
            # TODO: add message to in-memory set (but do this somewhere else...?)
            raise UniqueSetError(detail=str(e)) from e

        self.logger.info("[RedisClient]: Message published:\n%s", message)
