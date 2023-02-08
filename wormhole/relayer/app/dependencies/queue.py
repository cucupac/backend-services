import aio_pika
from aio_pika import RobustConnection
from aio_pika.abc import AbstractQueue

from app.dependencies import get_event_loop, get_logger
from app.settings import settings

connection = None
queue = None


async def get_queue() -> AbstractQueue:
    global queue  # pylint: disable = global-statement
    global connection  # pylint: disable = global-statement

    logger = get_logger()

    if queue is None:
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

        logger.info(message="[RabbitmqClient]: Established connection.")

        channel = await connection.channel()

        queue = await channel.declare_queue(settings.queue_name, durable=True)

        await queue.bind(settings.exchange_name, routing_key=settings.routing_key)

        logger.info(message="[RabbitmqClient]: Established queue.")

    return queue


async def get_connection() -> RobustConnection:
    return connection
