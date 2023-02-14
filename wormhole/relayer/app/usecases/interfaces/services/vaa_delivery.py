from abc import ABC, abstractmethod


class IVaaDelivery(ABC):
    @abstractmethod
    async def process(self, queue_message: bytes) -> None:
        """Process message from queue."""
