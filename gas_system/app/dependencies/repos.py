from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.fee_updates import FeeUpdateRepo
from app.infrastructure.db.repos.transactions import TransactionsRepo
from app.usecases.interfaces.repos.fee_updates import IFeeUpdateRepo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo


async def get_fee_update_repo() -> IFeeUpdateRepo:
    return FeeUpdateRepo(db=await get_or_create_database())


async def get_transactions_repo() -> ITransactionsRepo:
    return TransactionsRepo(db=await get_or_create_database())
