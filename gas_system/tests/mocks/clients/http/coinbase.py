from typing import Mapping, Union

from app.usecases.interfaces.clients.http.prices import IPriceClient
from tests import constants as constant


class MockPriceClient(IPriceClient):
    async def fetch_prices(self, chain_data: dict) -> Mapping[str, Union[str, int]]:
        """Fetches desired asset price in terms of many currencies."""

        return {"USD": constant.MOCK_USD_VALUES[chain_data["native"]]}
