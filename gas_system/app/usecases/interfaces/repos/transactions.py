from abc import ABC, abstractmethod

from app.usecases.schemas.transactions import TransactionsJoinRelays


class ITransactionsRepo(ABC):
    @abstractmethod
    async def retrieve_testing_by_chain_id(
        self, chain_id: int
    ) -> TransactionsJoinRelays:
        """Retrieves relays with status of `testing`."""
