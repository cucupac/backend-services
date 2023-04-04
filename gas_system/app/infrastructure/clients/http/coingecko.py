from typing import Any, Mapping, Optional, Union

from aiohttp import ClientSession

from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.schemas.prices import (
    APIErrorBody,
    PriceClientError,
    PriceClientException,
)


class CoingeckoClient(IPriceClient):
    def __init__(self, client_session: ClientSession, base_url: str):
        self.client_session = client_session
        self.base_url = base_url

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

    async def fetch_prices(self, chain_data: dict) -> Mapping[str, Union[str, int]]:
        """Fetches desired asset price in terms of USD."""

        response_json = await self.api_call(
            method="GET",
            endpoint=f"/price?ids={chain_data['coingecko_id']}&vs_currencies=usd&precision=18",
        )

        return response_json[chain_data["coingecko_id"]]
