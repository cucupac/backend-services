from app.dependencies import get_evm_client, get_example_repo
from app.usecases.interfaces.services.example import IExampleService
from app.usecases.services.example import ExampleService


async def get_example_service() -> IExampleService:
    """Instantiates and returns the Example Service."""

    transaction_repo = await get_example_repo()
    evm_client = await get_evm_client()

    return ExampleService(
        relays_repo=transaction_repo,
        evm_client=evm_client,
    )
