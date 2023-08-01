from abc import ABC, abstractmethod
from typing import Optional

from app.usecases.schemas.cross_chain_message import (
    LayerZeroMessageInDb,
    LzCompositeIndex,
    LzMessage,
    WhCompositeIndex,
    WhMessage,
    WormholeMessageInDb,
)


class IMessagesRepo(ABC):
    @abstractmethod
    async def create_layer_zero_message(
        self, cross_chain_transaction_id: int, message: LzMessage
    ) -> None:
        """Inserts a Layer Zero message."""

    @abstractmethod
    async def create_wormhole_message(
        self, cross_chain_transaction_id: int, message: WhMessage
    ) -> None:
        """Inserts a Wormhole message."""

    @abstractmethod
    async def retrieve_layer_zero_message(
        self, index: LzCompositeIndex
    ) -> Optional[LayerZeroMessageInDb]:
        """Retrieves a Layer Zero message."""

    @abstractmethod
    async def retrieve_wormhole_message(
        self, index: WhCompositeIndex
    ) -> Optional[WormholeMessageInDb]:
        """Retrieves a Wormhole message."""
