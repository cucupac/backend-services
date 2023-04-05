from typing import Mapping

from app.usecases.interfaces.clients.http.prices import IPriceClient
from tests import constants as constant


class MockPriceClient(IPriceClient):
    # TODO: once actual function is written, mock
    async def fetch_usd_prices(self) -> Mapping[str, float]:
        """Fetches desired asset price in terms of many currencies."""

        return constant.MOCK_USD_VALUES
