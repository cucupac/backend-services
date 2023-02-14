from typing import Optional

from app.infrastructure.clients.ws.websocket import WebSocket
from app.usecases.interfaces.clients.ws.websocket import IWebsocketClient
from app.usecases.schemas.relays import Status


class MockWebsocketClient(IWebsocketClient):
    async def open_connection(self, address: str, connection: WebSocket) -> None:
        """Open web socket connection and store it in dictionary."""

    async def close_connection(self, address: str) -> None:
        """Close web socket connection."""

    async def notify_client(
        self,
        address: str,
        status: Status,
        error: Optional[str],
        transaction_hash: Optional[str],
    ) -> None:
        """Notify client that action occured."""
