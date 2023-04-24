from abc import ABC, abstractmethod


class IVaaDelivery(ABC):
    @abstractmethod
    async def process(self, set_message: bytes) -> None:
        """Process message from unique set."""
