from databases import Database
from sqlalchemy import select

from app.infrastructure.db.models.mock_transactions import MOCK_TRANSACTIONS
from app.usecases.interfaces.repos.mock_transactions import IMockTransactionsRepo
from app.usecases.schemas.mock_transaction import MockTransactionInDb


class MockTransactionsRepo(IMockTransactionsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def retrieve(self, chain_id: int) -> MockTransactionInDb:
        """Retrieves mock transaction by chain ID."""

        query = select(MOCK_TRANSACTIONS).where(
            MOCK_TRANSACTIONS.c.chain_id == chain_id
        )

        result = await self.db.fetch_one(query)

        return MockTransactionInDb(**result)
