from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.fee_updates import FeeUpdatesRepo
from app.infrastructure.db.repos.mock_transactions import MockTransactionsRepo
from app.usecases.interfaces.repos.fee_updates import IFeeUpdatesRepo
from app.usecases.interfaces.repos.mock_transactions import IMockTransactionsRepo


async def get_fee_updates_repo() -> IFeeUpdatesRepo:
    return FeeUpdatesRepo(db=await get_or_create_database())


async def get_mock_transactions_repo() -> IMockTransactionsRepo:
    return MockTransactionsRepo(db=await get_or_create_database())
