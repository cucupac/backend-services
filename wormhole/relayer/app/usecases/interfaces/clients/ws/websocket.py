from abc import ABC, abstractmethod
from typing import Optional

from fastapi import WebSocket

from app.usecases.schemas.relays import Status


class IWebsocketClient(ABC):
    @abstractmethod
    async def open_connection(self, address: str, connection: WebSocket) -> None:
        """Open web socket connection and store it in dictionary."""

    @abstractmethod
    async def notify_client(
        self,
        address: str,
        status: Status,
        error: Optional[str],
        transaction_hash: Optional[str],
    ) -> None:
        """Notify client that action occured."""
