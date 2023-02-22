from app.dependencies import get_event_loop, get_remote_price_manager, logger
from app.usecases.tasks.fee_update import UpdateFeesTask


async def start_fee_update_task():
    loop = await get_event_loop()
    remote_price_manager = await get_remote_price_manager()

    get_update_fees_task = UpdateFeesTask(
        remote_price_manager=remote_price_manager, logger=logger
    )

    loop.create_task(get_update_fees_task.start_task())
