from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.relays import RelaysRepo
from app.infrastructure.db.repos.transactions import TransactionsRepo
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo


async def get_transactions_repo() -> ITransactionsRepo:
    return TransactionsRepo(db=await get_or_create_database())


async def get_relays_repo() -> IRelaysRepo:
    return RelaysRepo(db=await get_or_create_database())
