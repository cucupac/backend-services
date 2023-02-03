from abc import ABC, abstractmethod

from app.usecases.schemas.queue import QueueMessage


class IQueueClient(ABC):
    @abstractmethod
    async def publish(self, message: QueueMessage) -> None:
        """Publishes message to RabbitMQ."""
