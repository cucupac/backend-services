from abc import ABC, abstractmethod


class IQueueClient(ABC):
    @abstractmethod
    async def start_consumption(self) -> None:
        """Consumes message to RabbitMQ."""
