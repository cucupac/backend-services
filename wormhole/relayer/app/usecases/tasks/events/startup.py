from app.dependencies import (
    get_bridge_client,
    get_event_loop,
    get_evm_client,
    get_message_processor,
    get_relays_repo,
    logger,
)
from app.usecases.tasks.retry_failed import RetryFailedTask


async def start_retry_failed_task():
    loop = await get_event_loop()
    message_processor = await get_message_processor()
    evm_client = await get_evm_client()
    bridge_client = await get_bridge_client()
    relays_repo = await get_relays_repo()

    get_update_fees_task = RetryFailedTask(
        message_processor=message_processor,
        evm_client=evm_client,
        bridge_client=bridge_client,
        relays_repo=relays_repo,
        logger=logger,
    )

    loop.create_task(get_update_fees_task.start_task())
