from app.dependencies import (
    CHAIN_DATA,
    get_coingecko_client,
    get_fee_updates_repo,
    get_wormhole_bridge_client,
)
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.schemas.blockchain import Ecosystem
from app.usecases.schemas.bridges import Bridge
from app.usecases.services.remote_price_manager import RemotePriceManager


async def get_remote_price_manager(
    ecosystem: Ecosystem, bridge: Bridge
) -> IRemotePriceManager:
    """Instantiates and returns the RemotePriceManager."""

    coingecko_client = await get_coingecko_client()
    fee_update_repo = await get_fee_updates_repo()

    if ecosystem == Ecosystem.EVM:
        if bridge == Bridge.WORMHOLE:
            blockchain_clients = {}
            for ax_chain_id in CHAIN_DATA:
                wormhole_bridge_client = await get_wormhole_bridge_client(
                    source_ax_chain_id=ax_chain_id
                )
                blockchain_clients[ax_chain_id] = wormhole_bridge_client

    return RemotePriceManager(
        price_client=coingecko_client,
        blockchain_clients=blockchain_clients,
        fee_update_repo=fee_update_repo,
    )
