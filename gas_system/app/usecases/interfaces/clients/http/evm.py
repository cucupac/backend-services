from abc import ABC, abstractmethod

from app.usecases.schemas.evm import TransactionHash


class IEvmClient(ABC):
    @abstractmethod
    async def update(self, data: bytes, dest_chain_id: int) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
