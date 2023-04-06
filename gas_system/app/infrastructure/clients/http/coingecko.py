from typing import Any, Mapping, Optional

from aiohttp import ClientSession

from app.dependencies import CHAIN_DATA
from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.schemas.blockchain import Chains
from app.usecases.schemas.prices import (
    APIErrorBody,
    PriceClientError,
    PriceClientException,
)


class CoingeckoClient(IPriceClient):
    def __init__(self, client_session: ClientSession, base_url: str):
        self.client_session = client_session
        self.base_url = base_url
        self.id_lookup = {
            "ethereum": Chains.ETHEREUM.value,
            "binancecoin": Chains.BSC.value,
            "matic-network": Chains.POLYGON.value,
            "avalanche-2": Chains.AVALANCHE.value,
            "fantom": Chains.FANTOM.value,
            "celo": Chains.CELO.value,
        }

    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Mapping[str, str]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """Facilitate API call."""

        async with self.client_session.request(
            method,
            self.base_url + endpoint,
            headers=headers,
            json=json_body,
            verify_ssl=False,
        ) as response:
            try:
                response_json = await response.json()
            except Exception as e:
                response_text = await response.text()
                raise PriceClientException(
                    f"CoingeckoClient Error: Response status: {response.status}, Response Text: {response_text}"
                ) from e

            if response.status != 200:
                try:
                    error = APIErrorBody(**response_json)
                except Exception as e:
                    raise PriceClientException(
                        f"CoingeckoClient Error: Response status: {response.status}, Response JSON: {response_json}"
                    ) from e
                raise PriceClientError(
                    status=response.status,
                    detail=error.detail,
                )

            return response_json

    async def fetch_usd_prices(self) -> Mapping[str, float]:
        """Fetches desired asset price in terms of USD."""

        endpoint = "/api/v3/simple/price?ids="

        for index, coingecko_id in enumerate(self.id_lookup):
            endpoint += coingecko_id
            if index != len(self.id_lookup) - 1:
                endpoint += "%2C"
            else:
                endpoint += "&vs_currencies=usd&precision=18"

        response_json = await self.api_call(
            method="GET",
            endpoint=endpoint,
        )

        price_dict = dict()
        for coingecko_id, value in response_json.items():
            price_dict[CHAIN_DATA[self.id_lookup[coingecko_id]]["native"]] = value[
                "usd"
            ]

        return price_dict
