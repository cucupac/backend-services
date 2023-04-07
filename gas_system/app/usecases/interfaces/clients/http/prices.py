from abc import ABC, abstractmethod
from typing import Mapping


class IPriceClient(ABC):
    @abstractmethod
    async def fetch_usd_prices(self) -> Mapping[str, float]:
        """Fetches desired asset price in terms of many currencies."""
