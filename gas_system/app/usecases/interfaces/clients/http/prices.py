from abc import ABC, abstractmethod
from typing import Mapping


class IPriceClient(ABC):
    @abstractmethod
    async def fetch_prices(self, asset_symbol: str) -> Mapping[str, str]:
        """Fetches desired asset price in terms of many currencies."""
