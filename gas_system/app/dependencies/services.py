from app.dependencies import get_coinbase_client, get_evm_client, get_fee_update_repo
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.services.remote_price_manager import RemotePriceManager


async def get_remote_price_manager() -> IRemotePriceManager:
    """Instantiates and returns the RemotePriceManager."""

    coinbase_client = await get_coinbase_client()
    evm_client = await get_evm_client()
    fee_update_repo = await get_fee_update_repo()

    return RemotePriceManager(
        price_client=coinbase_client,
        blockchain_client=evm_client,
        fee_update_repo=fee_update_repo,
    )
