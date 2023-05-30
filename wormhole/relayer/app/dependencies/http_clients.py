from app.dependencies import CHAIN_DATA, WORMHOLE_BRIDGE_ABI, get_client_session, logger
from app.infrastructure.clients.evm import EvmClient
from app.infrastructure.clients.wormhole import WormholeClient
from app.settings import settings
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.interfaces.clients.evm import IEvmClient


async def get_evm_client(chain_id: int) -> IEvmClient:
    """Instantiate and return EVM client."""

    return EvmClient(
        abi=WORMHOLE_BRIDGE_ABI,
        chain_id=chain_id,
        rpc_url=CHAIN_DATA[chain_id]["rpc"],
        logger=logger,
    )


async def get_bridge_client() -> IBridgeClient:
    """Instantiate and return Coinbase client."""

    client_session = await get_client_session()

    return WormholeClient(
        client_session=client_session, base_url=settings.bridge_client_base_url
    )
