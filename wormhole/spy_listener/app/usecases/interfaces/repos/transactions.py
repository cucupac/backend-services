from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas.transactions import (
    CreateRepoAdapter,
    RetriveManyRepoAdapter,
    TransactionsJoinRelays,
)


class ITransactionsRepo(ABC):
    @abstractmethod
    async def create(self, transaction: CreateRepoAdapter) -> TransactionsJoinRelays:
        """Inserts and returns new transaction object."""

    @abstractmethod
    async def retrieve(
        self,
        transaction_id: int,
    ) -> Optional[TransactionsJoinRelays]:
        """Retrieve transaction object with relay information."""

    @abstractmethod
    async def retrieve_many(
        self,
        query_params: RetriveManyRepoAdapter,
    ) -> List[TransactionsJoinRelays]:
        """Retrieve transaction object with relay information."""
