import aio_pika
from aio_pika import ExchangeType, RobustConnection
from aio_pika.abc import AbstractExchange

from app.dependencies import get_event_loop, get_logger
from app.settings import settings

connection = None
exchange = None


async def get_exchange() -> AbstractExchange:
    global connection  # pylint: disable = global-statement
    global exchange  # pylint: disable = global-statement

    if connection is None:
        event_loop = await get_event_loop()

        connection = await aio_pika.connect_robust(
            "amqp://{username}:{password}@{host}:{port}".format(
                username=settings.rmq_username,
                password=settings.rmq_password,
                host=settings.rmq_host,
                port=settings.rmq_port,
            ),
            loop=event_loop,
        )

        logger = await get_logger()
        logger.info(message="[RabbitmqClient]: Connected to queue.")

        channel = await connection.channel(publisher_confirms=True)
        logger.info(message="[RabbitmqClient]: Established channel.")

        exchange = await channel.declare_exchange(
            settings.exchange_name, ExchangeType.DIRECT
        )
        logger.info(message="[RabbitmqClient]: Established exchange.")

    return exchange


async def get_connection() -> RobustConnection:
    return connection
