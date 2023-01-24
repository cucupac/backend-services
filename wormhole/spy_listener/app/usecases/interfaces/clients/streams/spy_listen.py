from abc import ABC, abstractmethod


class IStreamClient(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Starts GRPC connection."""
