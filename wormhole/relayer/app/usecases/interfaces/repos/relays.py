from abc import ABC, abstractmethod
from typing import List

from app.usecases.schemas.relays import UpdateJoinedRepoAdapter, UpdateRepoAdapter
from app.usecases.schemas.transactions import TransactionsJoinRelays


class IRelaysRepo(ABC):
    @abstractmethod
    async def update(self, relay: UpdateRepoAdapter) -> None:
        """Update relay object."""

    @abstractmethod
    async def update_relay_and_transaction(
        self, update_data: UpdateJoinedRepoAdapter
    ) -> None:
        """Update relay and transaction object."""

    @abstractmethod
    async def retrieve_failed(self) -> List[TransactionsJoinRelays]:
        """Retrieve all failed transactions that are not currently cached elsewhere."""
