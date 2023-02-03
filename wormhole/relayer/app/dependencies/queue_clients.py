from app.dependencies import get_logger, get_queue, get_vaa_delivery
from app.infrastructure.clients.queues.rabbitmq import RabbitmqClient
from app.usecases.interfaces.clients.queues.queue import IQueueClient


async def get_rabbitmq_client() -> IQueueClient:
    """Instantiate and return RabbitMQ client."""

    queue = await get_queue()
    logger = get_logger()
    vaa_delivery_service = await get_vaa_delivery()

    return RabbitmqClient(queue=queue, vaa_delivery=vaa_delivery_service, logger=logger)
