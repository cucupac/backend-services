import json

from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractExchange

from app.settings import settings
from app.usecases.interfaces.clients.queues.queue import IQueueClient
from app.usecases.interfaces.dependencies.logger import ILogger
from app.usecases.schemas.queue import QueueError, QueueMessage


class RabbitmqClient(IQueueClient):
    def __init__(self, exchange: AbstractExchange, logger: ILogger) -> None:
        self.exchange = exchange
        self.logger = logger

    async def publish(self, message: QueueMessage) -> None:
        try:
            result = await self.exchange.publish(
                Message(
                    body=json.dumps(message.dict()).encode(),
                    delivery_mode=DeliveryMode.PERSISTENT,
                ),
                routing_key=settings.routing_key,
                mandatory=True,
            )

        except Exception as e:
            self.logger.error(
                message="[RabbitmqClient]: Message was not published to RabbitMQ.\nError: %s"
                % str(e)
            )
            raise QueueError(detail=str(e))
        else:
            self.logger.info(
                message="[RabbitmqClient]: Message was successfully published and delivered to RabbitMQ:\n%s"
                % message
            )
