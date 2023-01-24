import json

from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractExchange

from app.dependencies import get_logger
from app.settings import settings
from app.usecases.interfaces.clients.queues.queue import IQueueClient
from app.usecases.schemas.queue import QueueError, QueueMessage


class RabbitmqClient(IQueueClient):
    def __init__(self, exchange: AbstractExchange) -> None:
        self.exchange = exchange

    async def publish(self, message: QueueMessage) -> None:
        """Publishes message to RabbitMQ."""

        try:
            is_delivered = await self.exchange.publish(
                Message(
                    body=json.dumps(message.dict()).encode(),
                    delivery_mode=DeliveryMode.PERSISTENT,
                ),
                routing_key=settings.routing_key,
            )

            logger = get_logger()
            if is_delivered:
                logger.info(message="[RabbitmqClient]: Message was successfully published and delivered to RabbitMQ:\n%s" % message)
            else:
                logger.info(message="[RabbitmqClient]: Message was published, but NOT successfully delivered to RabbitMQ.")
        except Exception as e:
            logger.error(message="[RabbitmqClient]: Message was not published to RabbitMQ.\nError: %s" % str(e))
            raise QueueError(detail=str(e))
