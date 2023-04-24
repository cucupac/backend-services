from app.dependencies import CHAIN_DATA, WORMHOLE_BRIDGE_ABI, logger
from app.infrastructure.clients.evm import EvmClient
from app.usecases.interfaces.clients.evm import IEvmClient


async def get_evm_client() -> IEvmClient:
    """Instantiate and return EVM client."""

    return EvmClient(
        abi=WORMHOLE_BRIDGE_ABI,
        chain_data=CHAIN_DATA,
        logger=logger,
    )
