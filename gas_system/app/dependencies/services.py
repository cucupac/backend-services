from app.dependencies import (
    get_coinbase_client,
    get_coingecko_client,
    get_evm_client,
    get_fee_update_repo,
)
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.schemas.blockchain import Ecosystem
from app.usecases.schemas.bridges import Bridge
from app.usecases.services.remote_price_manager import RemotePriceManager


async def get_remote_price_manager(
    ecosystem: Ecosystem, bridge: Bridge
) -> IRemotePriceManager:
    """Instantiates and returns the RemotePriceManager."""

    if ecosystem == Ecosystem.EVM:
        blockchain_client = await get_evm_client(bridge=bridge)

    coinbase_client = await get_coinbase_client()
    coingecko_client = await get_coingecko_client()
    fee_update_repo = await get_fee_update_repo()

    return RemotePriceManager(
        primary_price_client=coinbase_client,
        secondary_price_client=coingecko_client,
        blockchain_client=blockchain_client,
        fee_update_repo=fee_update_repo,
    )
