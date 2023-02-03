from abc import ABC, abstractmethod

from app.usecases.schemas.evm import TransactionHash


class IEvmClient(ABC):
    @abstractmethod
    async def deliver(
        self, vaa: bytes, dest_chain_id: int, dest_address: str
    ) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
