from app.dependencies import CHAIN_DATA, WORMHOLE_BRIDGE_ABI, get_client_session, logger
from app.infrastructure.clients.http.coingecko import CoingeckoClient
from app.infrastructure.clients.http.evm import EvmClient
from app.infrastructure.clients.http.wormhole_bridge import WormholeBridgeClient
from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.bridge import IBridgeClient
from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.schemas.blockchain import Chains
from app.usecases.schemas.bridges import Bridge
from app.usecases.schemas.fees import MinimumFees


async def get_evm_client(bridge: Bridge) -> IBlockchainClient:
    """Instantiate and return EVM client."""

    if bridge == Bridge.WORMHOLE:
        bridge_client = await get_wormhole_bridge_client()

    return EvmClient(
        bridge_client=bridge_client,
        chain_data=CHAIN_DATA,
        logger=logger,
    )


async def get_coingecko_client() -> IPriceClient:
    """Instantiate and return Coinbase client."""

    client_session = await get_client_session()

    return CoingeckoClient(
        client_session=client_session, base_url=settings.price_client_base_url
    )


async def get_wormhole_bridge_client() -> IBridgeClient:
    """Instantiate and return WormholeBridge client."""

    mock_set_send_fees_params = MinimumFees(remote_chain_ids=[], remote_fees=[])

    for chain in Chains:
        mock_set_send_fees_params.remote_chain_ids.append(chain.value)
        mock_set_send_fees_params.remote_fees.append(settings.mock_fee)

    return WormholeBridgeClient(
        address=settings.evm_wormhole_bridge,
        abi=WORMHOLE_BRIDGE_ABI,
        mock_set_send_fees_params=mock_set_send_fees_params,
    )
