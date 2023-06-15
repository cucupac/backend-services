from app.dependencies import (
    CHAIN_DATA,
    BRIDGE_DATA,
    WORMHOLE_BRIDGE_ABI,
    get_client_session,
    logger,
    get_transactions_repo,
)
from app.infrastructure.clients.http.coingecko import CoingeckoClient
from app.infrastructure.clients.http.evm_wormhole_bridge import WormholeBridgeEvmClient
from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.prices import IPriceClient


async def get_wormhole_bridge_client(source_chain_id: int) -> IBlockchainClient:
    """Instantiate and return WormholeBridge client."""

    transactions_repo = await get_transactions_repo()

    wormhole_chain_id = BRIDGE_DATA[source_chain_id]["wormhole"]["chain_id"]
    test_transaction = await transactions_repo.retrieve_testing_by_chain_id(
        chain_id=wormhole_chain_id
    )

    return WormholeBridgeEvmClient(
        abi=WORMHOLE_BRIDGE_ABI,
        chain_id=source_chain_id,
        rpc_url=CHAIN_DATA[source_chain_id]["rpc"],
        mock_payload=bytes.fromhex(test_transaction.relay_message),
        logger=logger,
    )


async def get_coingecko_client() -> IPriceClient:
    """Instantiate and return Coinbase client."""

    client_session = await get_client_session()

    return CoingeckoClient(
        client_session=client_session, base_url=settings.price_client_base_url
    )
