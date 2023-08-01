from abc import ABC, abstractmethod
from typing import List

from web3.types import TxReceipt


class IEvmClient(ABC):
    @abstractmethod
    async def fetch_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[LogReceipt]:
        """Fetches events emitted from given contract, for a given block range."""
