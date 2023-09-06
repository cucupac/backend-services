from app.dependencies import (
    CHAIN_DATA,
    get_block_records_repo,
    get_event_loop,
    get_evm_client,
    get_messages_repo,
    get_mints_repo,
    get_points_repo,
    get_tasks_repo,
    get_transactions_repo,
    logger,
)
from app.infrastructure.db.core import get_or_create_database
from app.usecases.schemas.blockchain import AxChains
from app.usecases.tasks.award_points import AwardPointsTask
from app.usecases.tasks.gather_mint_events import GatherMintEventsTask
from app.usecases.tasks.gather_transfer_events import GatherTransferEventsTask
from app.usecases.tasks.manage_locks import ManageLocksTask
from app.usecases.tasks.verify_transactions import VerifyTransactionsTask


async def start_gather_transfer_events_task() -> None:
    """Starts an ongoing task to gather on-chain transfer events."""

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

    gather_transfer_events_task = GatherTransferEventsTask(
        supported_evm_clients=supported_evm_clients,
        transactions_repo=transaction_repo,
        messages_repo=messages_repo,
        block_record_repo=block_record_repo,
        tasks_repo=tasks_repo,
        db=db,
        logger=logger,
    )

    loop.create_task(gather_transfer_events_task.start_task())


async def start_gather_mint_events_task() -> None:
    """Starts an ongoing task to gather on-chain mint events."""

    loop = await get_event_loop()
    db = await get_or_create_database()
    transaction_repo = await get_transactions_repo()
    mints_repo = await get_mints_repo()
    block_record_repo = await get_block_records_repo()
    tasks_repo = await get_tasks_repo()

    evm_client = await get_evm_client(ax_chain_id=AxChains.ETHEREUM)

    gather_mint_events_task = GatherMintEventsTask(
        evm_client=evm_client,
        transactions_repo=transaction_repo,
        mints_repo=mints_repo,
        block_record_repo=block_record_repo,
        tasks_repo=tasks_repo,
        db=db,
        logger=logger,
    )

    loop.create_task(gather_mint_events_task.start_task())


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


async def start_award_points_task() -> None:
    loop = await get_event_loop()
    tasks_repo = await get_tasks_repo()
    mints_repo = await get_mints_repo()
    points_repo = await get_points_repo()

    award_points_task = AwardPointsTask(
        points_repo=points_repo,
        mints_repo=mints_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )

    loop.create_task(award_points_task.start_task())
