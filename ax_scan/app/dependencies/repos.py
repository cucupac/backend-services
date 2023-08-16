from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.block_record import BlockRecordRepo
from app.infrastructure.db.repos.messages import MessagesRepo
from app.infrastructure.db.repos.tasks import TasksRepo
from app.infrastructure.db.repos.transactions import TransactionsRepo
from app.usecases.interfaces.repos.block_record import IBlockRecordRepo
from app.usecases.interfaces.repos.messages import IMessagesRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo


async def get_transactions_repo() -> ITransactionsRepo:
    return TransactionsRepo(db=await get_or_create_database())


async def get_messages_repo() -> IMessagesRepo:
    return MessagesRepo(db=await get_or_create_database())


async def get_block_records_repo() -> IBlockRecordRepo:
    return BlockRecordRepo(db=await get_or_create_database())


async def get_tasks_repo() -> ITasksRepo:
    return TasksRepo(db=await get_or_create_database())
