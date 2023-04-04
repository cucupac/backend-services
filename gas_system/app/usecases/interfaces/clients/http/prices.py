from abc import ABC, abstractmethod
from typing import Mapping, Union


class IPriceClient(ABC):
    @abstractmethod
    async def fetch_prices(self, chain_data: dict) -> Mapping[str, Union[str, int]]:
        """Fetches desired asset price in terms of many currencies."""
