from abc import ABC, abstractmethod

from app.usecases.schemas.bridge import BridgeMessage


class IBridgeClient(ABC):
    @abstractmethod
    async def fetch_bridge_message(
        self, emitter_address: str, emitter_chain_id: int, sequence: int
    ) -> BridgeMessage:
        """Fetches stored bridge messages from bridge provider."""
