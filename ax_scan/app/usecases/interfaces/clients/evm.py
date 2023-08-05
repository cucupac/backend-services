from abc import ABC, abstractmethod
from typing import List, Union

from web3.datastructures import AttributeDict

from app.usecases.schemas.events import SendToChain, ReceiveFromChain


class IEvmClient(ABC):
    @abstractmethod
    async def fetch_receipt(self, transaction_hash: str) -> AttributeDict:
        """Fetches the transaction receipt for a given transaction hash."""

    @abstractmethod
    async def fetch_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Union[SendToChain, ReceiveFromChain]]:
        """Fetches events emitted from given contract, for a given block range."""

    @abstractmethod
    async def fetch_latest_block_number(self) -> int:
        """Fetches the latest block number."""
