from app.dependencies import get_reddis_client, get_transactions_repo, logger
from app.usecases.interfaces.services.vaa_manager import IVaaManager
from app.usecases.services.vaa_manager import VaaManager


async def get_vaa_manager() -> IVaaManager:
    """Instantiates and returns the VAA Manager Service."""

    transaction_repo = await get_transactions_repo()
    unique_set_client = await get_reddis_client()

    return VaaManager(
        transactions_repo=transaction_repo, unique_set=unique_set_client, logger=logger
    )
