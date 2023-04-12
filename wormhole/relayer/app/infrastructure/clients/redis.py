import asyncio
from asyncio import AbstractEventLoop
from datetime import datetime, timezone
from logging import Logger

from redis import Redis, exceptions

from app.settings import settings
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery


class RedisClient(IUniqueSetClient):
    def __init__(
        self,
        vaa_delivery: IVaaDelivery,
        logger: Logger,
    ) -> None:
        self.connection = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
        )
        self.vaa_delivery = vaa_delivery
        self.script = """
        local items = redis.call("zrangebyscore", KEYS[1], "-inf", ARGV[1])
        if #items > 0 then
            redis.call("zrem", KEYS[1], unpack(items))
        end
        return items
        """
        self.logger = logger
        self.reconnecting = False

        if self.connection.ping():
            self.logger.info("[RedisClient]: Established connection.")

    async def start(self, loop: AbstractEventLoop) -> None:
        """Add consumption loop to event loop."""
        loop.create_task(self.start_consumption())

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
                self.logger.info("[RedisClient]: Reconnection successful...")
                return

    async def start_consumption(self) -> None:
        """Starts listening for messages to consume."""

        script_sha = self.connection.script_load(self.script)

        while True:
            await asyncio.sleep(settings.redis_consumption_frequency)
            current_date = datetime.now(timezone.utc)
            current_time = current_date.timestamp()
            max_score = current_time - settings.redis_min_message_age
            try:
                messages = self.connection.evalsha(
                    script_sha, 1, settings.redis_zset, max_score
                )
            except exceptions.ConnectionError:
                self.logger.error(
                    "[RedisClient]: Connection error, attempting reconnect..."
                )
                if not self.reconnecting:
                    await self.__reconnect()
            except exceptions.RedisError as e:
                self.logger.error("[RedisClient]: Unexpected error: %s", str(e))
            else:
                for message in messages:
                    await self.__on_message(message=message)

    async def __on_message(self, message: bytes) -> None:
        """Handle receiving an individual Redis message."""

        self.logger.info("[RedisClient]: Received message: %s.", str(message))

        await self.vaa_delivery.process(message=message)
