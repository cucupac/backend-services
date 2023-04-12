from app.dependencies import CHAIN_DATA, WORMHOLE_BRIDGE_ABI, logger
from app.infrastructure.clients.evm import EvmClient
from app.infrastructure.clients.wormhole_bridge import WormholeBridgeClient
from app.settings import settings
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.interfaces.clients.evm import IEvmClient


async def get_evm_client() -> IEvmClient:
    """Instantiate and return EVM client."""

    bridge_client = await get_wormhole_bridge_client()

    return EvmClient(
        bridge_client=bridge_client,
        chain_data=CHAIN_DATA,
        logger=logger,
    )


async def get_wormhole_bridge_client() -> IBridgeClient:
    """Instantiate and return WormholeBridge client."""

    return WormholeBridgeClient(
        address=settings.evm_wormhole_bridge,
        abi=WORMHOLE_BRIDGE_ABI,
    )
