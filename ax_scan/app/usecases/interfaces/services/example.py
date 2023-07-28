from abc import ABC, abstractmethod


class IExample(ABC):
    @abstractmethod
    async def example_function() -> None:
        """This is an example function."""
