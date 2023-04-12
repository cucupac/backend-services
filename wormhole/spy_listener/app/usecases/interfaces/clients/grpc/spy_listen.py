from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop


class IStreamClient(ABC):
    @abstractmethod
    async def start(self, loop: AbstractEventLoop) -> None:
        """Starts GRPC connection."""
