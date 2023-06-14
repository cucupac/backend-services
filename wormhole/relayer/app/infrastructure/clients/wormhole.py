from typing import Any, Mapping, Optional

from aiohttp import ClientSession

from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.schemas.bridge import (
    APIErrorBody,
    BridgeClientError,
    BridgeClientException,
    BridgeMessage,
    NotFoundException,
)


class WormholeClient(IBridgeClient):
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
                raise BridgeClientException(
                    f"WormholeClient Error: Response status: {response.status}, Response Text: {response_text}"
                ) from e

            if response.status != 200:
                if response.status == 404:
                    raise NotFoundException()
                try:
                    error = APIErrorBody(**response_json)
                except Exception as e:
                    raise BridgeClientException(
                        f"WormholeClient Error: Response status: {response.status}, Response JSON: {response_json}"
                    ) from e
                raise BridgeClientError(
                    status=response.status,
                    detail=error.detail,
                )

            return response_json

    async def fetch_bridge_message(
        self, emitter_address: str, emitter_chain_id: int, sequence: int
    ) -> BridgeMessage:
        """Fetches stored bridge messages from bridge provider."""

        truncated_emitter_address = emitter_address[2:]

        response_json = await self.api_call(
            method="GET",
            endpoint=f"/v1/signed_vaa/{emitter_chain_id}/000000000000000000000000{truncated_emitter_address}/{sequence}",
        )

        return BridgeMessage(b64_message=response_json["vaaBytes"])
