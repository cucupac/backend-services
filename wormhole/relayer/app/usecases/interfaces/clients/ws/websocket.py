from abc import ABC, abstractmethod

from fastapi import WebSocket


class IWebsocketClient(ABC):
    @abstractmethod
    async def open_connection(self, address: str, connection: WebSocket) -> None:
        """Open web socket connection and store it in dictionary."""

    @abstractmethod
    async def close_connection(self, address: str) -> None:
        """Close web socket connection."""

    @abstractmethod
    async def notify_client(self, address: str, transaction_hash: str) -> None:
        """Notify client that action occured."""
