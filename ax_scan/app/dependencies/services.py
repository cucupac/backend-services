from app.usecases.interfaces.services.example import IExample
from app.usecases.services.example import ExampleService


async def get_example_service() -> IExample:
    """Instantiates and returns the ExampleService."""

    return ExampleService()
