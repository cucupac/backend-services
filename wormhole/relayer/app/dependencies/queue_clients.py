from app.dependencies import get_queue, get_vaa_delivery, logger
from app.infrastructure.clients.amqp.rabbitmq import RabbitmqClient
from app.usecases.interfaces.clients.amqp.queue import IQueueClient


async def get_rabbitmq_client() -> IQueueClient:
    """Instantiate and return RabbitMQ client."""

    queue = await get_queue()
    vaa_delivery_service = await get_vaa_delivery()

    return RabbitmqClient(queue=queue, vaa_delivery=vaa_delivery_service, logger=logger)
