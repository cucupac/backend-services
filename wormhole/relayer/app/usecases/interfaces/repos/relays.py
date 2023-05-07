from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas.relays import UpdateJoinedRepoAdapter, UpdateRepoAdapter
from app.usecases.schemas.transactions import CreateRepoAdapter, TransactionsJoinRelays


class IRelaysRepo(ABC):
    @abstractmethod
    async def create(self, transaction: CreateRepoAdapter) -> None:
        """Creates new transaction and relay object."""

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

    @abstractmethod
    async def get_latest_sequence(
        self,
        emitter_address: str,
        source_chain_id: int,
    ) -> Optional[TransactionsJoinRelays]:
        """Get the latest transaction for the given emitter_address and source_chain_id."""
