from abc import ABC, abstractmethod

from app.usecases.schemas.unique_set import UniqueSetMessage


class IUniqueSetClient(ABC):
    @abstractmethod
    async def publish(self, message: UniqueSetMessage) -> int:
        """Publishes message to unique set."""
