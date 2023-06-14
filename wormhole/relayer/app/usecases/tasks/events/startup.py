from app.dependencies import (
    CHAIN_DATA,
    get_bridge_client,
    get_event_loop,
    get_evm_client,
    get_message_processor,
    get_relays_repo,
    get_tasks_repo,
    logger,
)
from app.usecases.tasks.gather_missed import GatherMissedVaasTask
from app.usecases.tasks.gather_pending import GatherPendingVaasTask
from app.usecases.tasks.manage_locks import ManageLocksTask
from app.usecases.tasks.retry_failed import RetryFailedTask
from app.usecases.tasks.verify_delivery import VerifyDeliveryTask


async def start_retry_failed_task() -> None:
    loop = await get_event_loop()
    message_processor = await get_message_processor()
    bridge_client = await get_bridge_client()
    relays_repo = await get_relays_repo()
    tasks_repo = await get_tasks_repo()

    supported_evm_clients = {}
    for chain_id in CHAIN_DATA:
        evm_client = await get_evm_client(chain_id=chain_id)
        supported_evm_clients[chain_id] = evm_client

    retry_failed_task = RetryFailedTask(
        message_processor=message_processor,
        supported_evm_clients=supported_evm_clients,
        bridge_client=bridge_client,
        relays_repo=relays_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )

    loop.create_task(retry_failed_task.start_task())


async def start_gather_missed_task() -> None:
    loop = await get_event_loop()
    message_processor = await get_message_processor()
    bridge_client = await get_bridge_client()
    relays_repo = await get_relays_repo()
    tasks_repo = await get_tasks_repo()

    gather_missed_task = GatherMissedVaasTask(
        message_processor=message_processor,
        bridge_client=bridge_client,
        relays_repo=relays_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )

    loop.create_task(gather_missed_task.start_task())


async def start_gather_pending_task() -> None:
    loop = await get_event_loop()
    relays_repo = await get_relays_repo()
    tasks_repo = await get_tasks_repo()

    gather_pending_task = GatherPendingVaasTask(
        relays_repo=relays_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )

    loop.create_task(gather_pending_task.start_task())


async def start_verify_delivery_task() -> None:
    loop = await get_event_loop()
    relays_repo = await get_relays_repo()
    tasks_repo = await get_tasks_repo()

    supported_evm_clients = {}
    for chain_id in CHAIN_DATA:
        evm_client = await get_evm_client(chain_id=chain_id)
        supported_evm_clients[chain_id] = evm_client

    verify_delivery_task = VerifyDeliveryTask(
        supported_evm_clients=supported_evm_clients,
        relays_repo=relays_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )

    loop.create_task(verify_delivery_task.start_task())


async def start_manage_locks_task() -> None:
    loop = await get_event_loop()
    tasks_repo = await get_tasks_repo()

    manage_locks_task = ManageLocksTask(tasks_repo=tasks_repo, logger=logger)

    loop.create_task(manage_locks_task.start_task())
