from aio_pika.abc import AbstractIncomingMessage, AbstractQueue

from app.usecases.interfaces.clients.queues.queue import IQueueClient
from app.usecases.interfaces.dependencies.logger import ILogger
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.schemas.queue import QueueError


class RabbitmqClient(IQueueClient):
    def __init__(
        self, queue: AbstractQueue, vaa_delivery: IVaaDelivery, logger: ILogger
    ) -> None:
        self.queue = queue
        self.logger = logger
        self.vaa_delivery = vaa_delivery

    async def start_consumption(self) -> None:
        """Consumes messages from RabbitMQ."""

        # Start listening
        try:
            await self.queue.consume(self.__on_message)
        except Exception as e:
            self.logger.error(
                message="[RabbitmqClient]: Message not consumed.\nError: %s"
                % str(e)
            )
            raise QueueError(detail=str(e))
        else:
            self.logger.error(
                message="[RabbitmqClient]: Listening for incoming messages."
            )

    async def __on_message(self, message: AbstractIncomingMessage) -> None:
        """Handle receiving an RMQ message."""

        async with message.process():
            self.logger.info(
                message="[RabbitmqClient]: Received message: %s." % str(message.body)
            )

            await self.vaa_delivery.process(queue_message=message.body)
