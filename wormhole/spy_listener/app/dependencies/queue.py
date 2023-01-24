import aio_pika
from aio_pika import ExchangeType, RobustConnection
from aio_pika.abc import AbstractExchange

from app.dependencies import get_event_loop, get_logger
from app.settings import settings

channel = None
connection = None
exchange = None


async def connect_to_queue() -> AbstractExchange:
    global channel  # pylint: disable = global-statement
    global connection  # pylint: disable = global-statement
    global exchange  # pylint: disable = global-statement

    if channel is None:
        event_loop = await get_event_loop()

        connection = await aio_pika.connect_robust(
            f"amqp://{settings.rabbitmq_username}:{settings.rabbitmq_password}@{settings.rabbitmq_host}:{settings.rabbitmq_port}/%2F",
            loop=event_loop,
        )

        logger = get_logger()
        logger.info(message="[RabbitmqClient]: Connected to queue!")

        channel = await connection.channel()

        logger.info(message="[RabbitmqClient]: Established queue channel!")

        exchange = await channel.declare_exchange(
            settings.exchange_name, ExchangeType.DIRECT
        )

        logger.info(message="[RabbitmqClient]: Established queue exchange!")

    return exchange


async def get_connection() -> RobustConnection:
    return connection


async def get_channel() -> RobustConnection:
    return channel


async def get_exchange() -> RobustConnection:
    return exchange