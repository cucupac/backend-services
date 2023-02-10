from aio_pika import RobustConnection, connect_robust
from aio_pika.abc import AbstractQueue

from app.dependencies import get_event_loop, logger
from app.settings import settings

connection = None
queue = None


async def get_queue() -> AbstractQueue:
    global queue  # pylint: disable = global-statement
    global connection  # pylint: disable = global-statement

    if queue is None:
        event_loop = await get_event_loop()

        connection = await connect_robust(
            f"amqp://{settings.rmq_username}:{settings.rmq_password}@{settings.rmq_host}:{settings.rmq_port}",
            loop=event_loop,
        )

        logger.info("[RabbitmqClient]: Established connection.")

        channel = await connection.channel()

        queue = await channel.declare_queue(settings.queue_name, durable=True)

        await queue.bind(settings.exchange_name, routing_key=settings.routing_key)

        logger.info("[RabbitmqClient]: Established queue.")

    return queue


async def get_connection() -> RobustConnection:
    return connection
