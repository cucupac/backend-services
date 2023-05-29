from abc import ABC, abstractmethod

from web3.types import TxReceipt

from app.usecases.schemas.blockchain import TransactionHash


class IEvmClient(ABC):
    @abstractmethod
    async def deliver(self, payload: str, dest_chain_id: int) -> TransactionHash:
        """Sends transaction to the destination blockchain."""

    @abstractmethod
    async def fetch_receipt(self, transaction_hash, dest_chain_id) -> TxReceipt:
        """Fetches the transaction receipt for a given transaction hash."""
