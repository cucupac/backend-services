from app.dependencies import get_exchange, get_logger
from app.infrastructure.clients.queues.rabbitmq import RabbitmqClient
from app.usecases.interfaces.clients.queues.queue import IQueueClient


async def get_rmq_client() -> IQueueClient:
    """Instantiate and return queue client."""

    exchange = await get_exchange()
    logger = await get_logger()

    return RabbitmqClient(exchange=exchange, logger=logger)
