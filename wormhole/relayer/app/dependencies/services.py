from app.dependencies import (
    CHAIN_DATA,
    get_evm_client,
    get_relays_repo,
    logger,
)
from app.usecases.interfaces.services.message_processor import IVaaProcessor
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.services.message_processor import MessageProcessor
from app.usecases.services.vaa_delivery import VaaDelivery


async def get_vaa_delivery() -> IVaaDelivery:
    """Instantiates and returns the VAA Delivery Service."""

    relays_repo = await get_relays_repo()

    supported_evm_clients = {}
    for chain_id in CHAIN_DATA:
        evm_client = await get_evm_client(chain_id=chain_id)
        supported_evm_clients[chain_id] = evm_client

    return VaaDelivery(
        relays_repo=relays_repo,
        supported_evm_clients=supported_evm_clients,
        logger=logger,
    )


async def get_message_processor() -> IVaaProcessor:
    """Instantiates and returns the Message Processor Service."""

    return MessageProcessor()
