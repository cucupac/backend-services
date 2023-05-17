from app.dependencies import (
    get_bridge_client,
    get_event_loop,
    get_evm_client,
    get_message_processor,
    get_relays_repo,
    logger,
)
from app.usecases.tasks.gather_missed import GatherMissedVaasTask
from app.usecases.tasks.gather_pending import GatherPendingVaasTask
from app.usecases.tasks.retry_failed import RetryFailedTask


async def start_retry_failed_task() -> None:
    loop = await get_event_loop()
    message_processor = await get_message_processor()
    evm_client = await get_evm_client()
    bridge_client = await get_bridge_client()
    relays_repo = await get_relays_repo()

    retry_failed_task = RetryFailedTask(
        message_processor=message_processor,
        evm_client=evm_client,
        bridge_client=bridge_client,
        relays_repo=relays_repo,
        logger=logger,
    )

    loop.create_task(retry_failed_task.start_task())


async def start_gather_missed_task() -> None:
    loop = await get_event_loop()
    message_processor = await get_message_processor()
    bridge_client = await get_bridge_client()
    relays_repo = await get_relays_repo()

    gather_missed_task = GatherMissedVaasTask(
        message_processor=message_processor,
        bridge_client=bridge_client,
        relays_repo=relays_repo,
        logger=logger,
    )

    loop.create_task(gather_missed_task.start_task())


async def start_gather_pending_task() -> None:
    loop = await get_event_loop()
    relays_repo = await get_relays_repo()

    gather_pending_task = GatherPendingVaasTask(
        relays_repo=relays_repo,
        logger=logger,
    )

    loop.create_task(gather_pending_task.start_task())
