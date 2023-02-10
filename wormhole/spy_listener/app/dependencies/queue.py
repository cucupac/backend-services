from aio_pika import ExchangeType, RobustConnection, connect_robust
from aio_pika.abc import AbstractExchange

from app.dependencies import get_event_loop, logger
from app.settings import settings

connection = None
exchange = None


async def get_exchange() -> AbstractExchange:
    global connection  # pylint: disable = global-statement
    global exchange  # pylint: disable = global-statement

    if connection is None:
        event_loop = await get_event_loop()

        connection = await connect_robust(
            f"amqp://{settings.rmq_username}:{settings.rmq_password}@{settings.rmq_host}:{settings.rmq_port}",
            loop=event_loop,
        )

        logger.info("[RabbitmqClient]: Established connection.")

        channel = await connection.channel(
            publisher_confirms=True, on_return_raises=True
        )
        logger.info("[RabbitmqClient]: Established channel.")

        exchange = await channel.declare_exchange(
            settings.exchange_name, ExchangeType.DIRECT
        )
        logger.info("[RabbitmqClient]: Established exchange.")

    return exchange


async def get_connection() -> RobustConnection:
    return connection
