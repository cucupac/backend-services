from app.dependencies import (
    CHAIN_DATA,
    get_block_records_repo,
    get_event_loop,
    get_evm_client,
    get_messages_repo,
    get_tasks_repo,
    get_transactions_repo,
    logger,
)
from app.infrastructure.db.core import get_or_create_database
from app.usecases.tasks.gather_events import GatherEventsTask
from app.usecases.tasks.manage_locks import ManageLocksTask
from app.usecases.tasks.verify_transactions import VerifyTransactionsTask


async def start_gather_events_task() -> None:
    """Starts an ongoing task to gather on-chain events."""

    loop = await get_event_loop()
    db = await get_or_create_database()
    transaction_repo = await get_transactions_repo()
    messages_repo = await get_messages_repo()
    block_record_repo = await get_block_records_repo()
    tasks_repo = await get_tasks_repo()

    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        evm_client = await get_evm_client(ax_chain_id=ax_chain_id)
        supported_evm_clients[ax_chain_id] = evm_client

    gather_events_task = GatherEventsTask(
        supported_evm_clients=supported_evm_clients,
        transactions_repo=transaction_repo,
        messages_repo=messages_repo,
        block_record_repo=block_record_repo,
        tasks_repo=tasks_repo,
        db=db,
        logger=logger,
    )

    loop.create_task(gather_events_task.start_task())


async def start_verify_transactions_task() -> None:
    """Starts an ongoing task to verify transactions."""

    loop = await get_event_loop()
    transaction_repo = await get_transactions_repo()
    tasks_repo = await get_tasks_repo()

    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        evm_client = await get_evm_client(ax_chain_id=ax_chain_id)
        supported_evm_clients[ax_chain_id] = evm_client

    verify_transactions_task = VerifyTransactionsTask(
        supported_evm_clients=supported_evm_clients,
        transactions_repo=transaction_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )

    loop.create_task(verify_transactions_task.start_task())


async def start_manage_locks_task() -> None:
    loop = await get_event_loop()
    tasks_repo = await get_tasks_repo()

    manage_locks_task = ManageLocksTask(tasks_repo=tasks_repo, logger=logger)

    loop.create_task(manage_locks_task.start_task())
