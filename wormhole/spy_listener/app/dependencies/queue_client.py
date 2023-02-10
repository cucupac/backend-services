from app.dependencies import get_exchange, logger
from app.infrastructure.clients.amqp.rabbitmq import RabbitmqClient
from app.usecases.interfaces.clients.amqp.queue import IQueueClient


async def get_rmq_client() -> IQueueClient:
    """Instantiate and return queue client."""

    exchange = await get_exchange()

    return RabbitmqClient(exchange=exchange, logger=logger)
