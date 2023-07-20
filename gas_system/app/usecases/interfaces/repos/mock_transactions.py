from abc import ABC, abstractmethod

from app.usecases.schemas.mock_transaction import MockTransactionInDb


class IMockTransactionsRepo(ABC):
    @abstractmethod
    async def retrieve(self, chain_id: int) -> MockTransactionInDb:
        """Retrieves mock transaction by chain ID."""
