from app.dependencies import CHAIN_DATA, WORMHOLE_BRIDGE_ABI, get_client_session, logger
from app.infrastructure.clients.http.coinbase import CoinbaseClient
from app.infrastructure.clients.http.evm import EvmClient
from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.schemas.fees import Chains, MinimumFees


async def get_evm_client() -> IBlockchainClient:
    """Instantiate and return EVM client."""

    mock_set_send_fees_params = MinimumFees(remote_chain_ids=[], fees=[])

    for chain in Chains:
        mock_set_send_fees_params.remote_chain_ids.append(chain.value)
        mock_set_send_fees_params.fees.append(settings.mock_fee)

    return EvmClient(
        abi=WORMHOLE_BRIDGE_ABI,
        chain_data=CHAIN_DATA,
        mock_set_send_fees_params=mock_set_send_fees_params,
        logger=logger,
    )


async def get_coinbase_client() -> IPriceClient:
    """Instantiate and return Coinbase client."""

    client_session = await get_client_session()

    return CoinbaseClient(
        client_session=client_session, base_url=settings.price_client_base_url
    )
