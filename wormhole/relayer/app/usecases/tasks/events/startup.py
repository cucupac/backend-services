from app.dependencies import (
    get_event_loop,
    get_evm_client,
    get_bridge_client,
    get_relays_repo,
    logger,
)
from app.usecases.tasks.retry_queued import RetryQueuedTask


async def start_retry_queued_task():
    loop = await get_event_loop()
    evm_client = await get_evm_client()
    bridge_client = await get_bridge_client()
    relays_repo = await get_relays_repo()

    get_update_fees_task = RetryQueuedTask(
        evm_client=evm_client,
        bridge_client=bridge_client,
        relays_repo=relays_repo,
        logger=logger,
    )

    loop.create_task(get_update_fees_task.start_task())
