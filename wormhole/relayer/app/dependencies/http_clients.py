from app.dependencies import CHAIN_DATA, WORMHOLE_BRIDGE_ABI, logger, get_client_session
from app.infrastructure.clients.evm import EvmClient
from app.infrastructure.clients.wormhole import WormholeClient
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.clients.bridge import IBridgeClient


from settings import settings


async def get_evm_client() -> IEvmClient:
    """Instantiate and return EVM client."""

    return EvmClient(
        abi=WORMHOLE_BRIDGE_ABI,
        chain_data=CHAIN_DATA,
        logger=logger,
    )


async def get_bridge_client() -> IBridgeClient:
    """Instantiate and return Coinbase client."""

    client_session = await get_client_session()

    return WormholeClient(
        client_session=client_session, base_url=settings.bridge_client_base_url
    )
