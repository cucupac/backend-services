from typing import Optional
from abc import ABC, abstractmethod

from app.usecases.schemas.cross_chain_message import (
    LzMessage,
    WhMessage,
    LzCompositeIndex,
    WhCompositeIndex,
    LayerZeroMessageInDb,
    WormholeMessageInDb,
)


class IMessagesRepo(ABC):
    @abstractmethod
    async def create_layer_zero_message(self, message: LzMessage) -> None:
        """Inserts a Layer Zero message."""

    @abstractmethod
    async def create_wormhole_message(self, message: WhMessage) -> None:
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
