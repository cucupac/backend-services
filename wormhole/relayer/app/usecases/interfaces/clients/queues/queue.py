from abc import ABC, abstractmethod

from app.usecases.schemas.queue import QueueMessage


class IQueueClient(ABC):
    @abstractmethod
    async def start_consumption(self) -> None:
        """Consumes message to RabbitMQ."""
