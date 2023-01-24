from app.dependencies import connect_to_queue
from app.infrastructure.clients.queues.rabbitmq import RabbitmqClient
from app.usecases.interfaces.clients.queues.queue import IQueueClient


async def get_rabbitmq_client() -> IQueueClient:
    """Instantiate and return Stream client."""

    exchange = await connect_to_queue()

    return RabbitmqClient(exchange=exchange)
