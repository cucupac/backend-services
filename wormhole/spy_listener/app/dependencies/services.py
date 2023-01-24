from app.dependencies import get_rabbitmq_client, get_transactions_repo
from app.usecases.interfaces.services.vaa_manager import IVaaManager
from app.usecases.services.vaa_manager import VaaManager


async def get_vaa_manager() -> IVaaManager:
    """Instantiates and returns the Challenge Validation Service."""

    transaction_repo = await get_transactions_repo()
    queue_client = await get_rabbitmq_client()

    return VaaManager(transactions_repo=transaction_repo, queue=queue_client)
