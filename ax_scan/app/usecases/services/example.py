from app.settings import settings
from app.usecases.interfaces.services.example import IExample


class ExampleService(IExample):
    def __init__(
        self,
    ):
        pass

    async def example_function(self) -> None:
        """Does something."""
