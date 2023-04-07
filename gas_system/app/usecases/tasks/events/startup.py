"""Current approach: Give each bridge contract its own, idependent asynchronous task.

=> Each task will need to specify: blockchain and the bridge contract
=> That get_remote_price_manager() should take parameter for both

If there are bridge contracts on the same blockchain type, then the evm client
should be able to distinguish between them (the client should not be tightly coupled)
"""


from app.dependencies import get_event_loop, get_remote_price_manager, logger
from app.usecases.schemas.blockchain import Ecosystem
from app.usecases.schemas.bridges import Bridge
from app.usecases.tasks.fee_update import UpdateFeesTask


async def evm_wormhole_bridge_fee_updates() -> None:
    loop = await get_event_loop()

    remote_price_manager = await get_remote_price_manager(
        ecosystem=Ecosystem.EVM, bridge=Bridge.WORMHOLE
    )

    get_update_fees_task = UpdateFeesTask(
        remote_price_manager=remote_price_manager, logger=logger
    )

    loop.create_task(get_update_fees_task.start_task())


async def start_fee_update_tasks() -> None:
    await evm_wormhole_bridge_fee_updates()
