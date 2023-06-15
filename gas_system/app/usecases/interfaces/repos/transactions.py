from abc import ABC, abstractmethod
from typing import List

from app.usecases.schemas.transactions import TransactionsJoinRelays


class ITransactionsRepo(ABC):
    @abstractmethod
    async def retrieve_testing(self, chain_id: int) -> TransactionsJoinRelays:
        """Retrieves relays with status of `testing`."""
