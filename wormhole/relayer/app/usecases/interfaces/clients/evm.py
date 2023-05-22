from abc import ABC, abstractmethod

from app.usecases.schemas.blockchain import TransactionHash


class IEvmClient(ABC):
    @abstractmethod
    async def deliver(self, payload: str, dest_chain_id: int) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
