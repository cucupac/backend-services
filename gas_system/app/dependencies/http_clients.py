from app.dependencies import CHAIN_DATA, WORMHOLE_BRIDGE_ABI, get_client_session, logger
from app.infrastructure.clients.http.coingecko import CoingeckoClient
from app.infrastructure.clients.http.evm_wormhole_bridge import WormholeBridgeEvmClient
from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.schemas.fees import MinimumFees


async def get_wormhole_bridge_client(source_chain_id: int) -> IBlockchainClient:
    """Instantiate and return WormholeBridge client."""

    mock_set_send_fees_params = MinimumFees(remote_chain_ids=[], remote_fees=[])

    for dest_chain_id in CHAIN_DATA:
        if dest_chain_id != source_chain_id:
            mock_set_send_fees_params.remote_chain_ids.append(dest_chain_id)
            mock_set_send_fees_params.remote_fees.append(settings.mock_fee)

    return WormholeBridgeEvmClient(
        abi=WORMHOLE_BRIDGE_ABI,
        chain_id=source_chain_id,
        rpc_url=CHAIN_DATA[source_chain_id]["rpc"],
        mock_set_send_fees_params=mock_set_send_fees_params,
        logger=logger,
    )


async def get_coingecko_client() -> IPriceClient:
    """Instantiate and return Coinbase client."""

    client_session = await get_client_session()

    return CoingeckoClient(
        client_session=client_session, base_url=settings.price_client_base_url
    )
