from app.dependencies import (
    get_evm_client,
    get_relays_repo,
    get_websocket_client,
    logger,
)
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.services.vaa_delivery import VaaDelivery


async def get_vaa_delivery() -> IVaaDelivery:
    """Instantiates and returns the VAA Delivery Service."""

    relays_repo = await get_relays_repo()
    evm_client = await get_evm_client()
    websocket_client = await get_websocket_client()

    return VaaDelivery(
        relays_repo=relays_repo,
        evm_client=evm_client,
        websocket_client=websocket_client,
        logger=logger,
    )
