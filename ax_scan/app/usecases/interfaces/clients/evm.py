from abc import ABC, abstractmethod
from typing import List, Union

from app.usecases.schemas.blockchain import TransactionReceipt
from app.usecases.schemas.events import Mint, ReceiveFromChain, SendToChain


class IEvmClient(ABC):
    @abstractmethod
    async def fetch_receipt(self, transaction_hash: str) -> TransactionReceipt:
        """Fetches the transaction receipt for a given transaction hash."""

    @abstractmethod
    async def fetch_transfer_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Union[SendToChain, ReceiveFromChain]]:
        """Fetches cross-chain transfer events emitted from given contract, for a given block range."""

    @abstractmethod
    async def fetch_mint_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Mint]:
        """Fetches mint events emitted from given contract, for a given block range."""

    @abstractmethod
    async def fetch_latest_block_number(self) -> int:
        """Fetches the latest block number."""
