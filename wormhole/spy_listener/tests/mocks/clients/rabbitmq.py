from enum import Enum

from app.usecases.interfaces.clients.amqp.queue import IQueueClient
from app.usecases.schemas.queue import QueueError, QueueMessage
from tests import constants as constant


class QueueResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class MockRabbitmqClient(IQueueClient):
    def __init__(self, result: QueueResult) -> None:
        self.result = result

    async def publish(self, message: QueueMessage) -> None:
        """Publishes message to RabbitMQ."""
        if self.result == QueueResult.SUCCESS:
            return
        elif self.result == QueueResult.FAILURE:
            raise QueueError(detail=constant.QUEUE_ERROR_DETAIL)
