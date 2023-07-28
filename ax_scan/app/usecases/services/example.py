from app.usecases.interfaces.services.example import IExample
from app.settings import settings


class ExampleService(IExample):
    def __init__(
        self,
    ):
        pass

    async def example_function(self) -> None:
        """Does something."""
