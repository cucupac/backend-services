import json

from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractExchange
from pamqp.commands import Basic

from app.settings import settings
from app.usecases.interfaces.clients.amqp.queue import IQueueClient
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

            if not isinstance(result, Basic.Ack):
                raise Exception("Ack was not returned for publish.\n%s" % str(result))

        except Exception as e:
            self.logger.error(
                message="[RabbitmqClient]: Message not published.\nError: %s" % str(e)
            )
            raise QueueError(detail=str(e))

        self.logger.info(message="[RabbitmqClient]: Message published:\n%s" % message)