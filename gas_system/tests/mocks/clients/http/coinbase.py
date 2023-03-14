from typing import Mapping

from app.usecases.interfaces.clients.http.prices import IPriceClient
from tests import constants as constant


class MockPriceClient(IPriceClient):
    async def fetch_prices(self, asset_symbol: str) -> Mapping[str, str]:
        """Fetches desired asset price in terms of many currencies."""

        return {"USD": constant.MOCK_USD_VALUES[asset_symbol]}
