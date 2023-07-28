from typing import Optional

from databases import Database
from sqlalchemy import and_

from app.infrastructure.db.models.layer_zero_messages import LAYER_ZERO_MESSAGES
from app.infrastructure.db.models.wormhole_messages import WORMHOLE_MESSAGES
from app.usecases.interfaces.repos.messages import IMessagesRepo
from app.usecases.schemas.cross_chain_message import (
    LzMessage,
    WhMessage,
    LzCompositeIndex,
    WhCompositeIndex,
    LayerZeroMessageInDb,
    WormholeMessageInDb,
)


class MessagesRepo(IMessagesRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create_layer_zero_message(self, message: LzMessage) -> None:
        """Inserts a Layer Zero message."""

        lz_messages_insert_stmt = LAYER_ZERO_MESSAGES.insert().values(
            emitter_address=message.emitter_address,
            source_chain_id=message.source_chain_id,
            dest_chain_id=message.dest_chain_id,
            nonce=message.message_id,
        )

        await self.db.execute(lz_messages_insert_stmt)

    async def create_wormhole_message(self, message: WhMessage) -> None:
        """Inserts a Wormhole message."""

        wh_messages_insert_stmt = WORMHOLE_MESSAGES.insert().values(
            emitter_address=message.emitter_address,
            source_chain_id=message.source_chain_id,
            sequence=message.message_id,
        )

        await self.db.execute(wh_messages_insert_stmt)

    async def retrieve_layer_zero_message(
        self, index: LzCompositeIndex
    ) -> Optional[LayerZeroMessageInDb]:
        """Retrieves a Layer Zero message."""

        query = LAYER_ZERO_MESSAGES.select().where(
            and_(
                LAYER_ZERO_MESSAGES.c.emitter_address == index.emitter_address,
                LAYER_ZERO_MESSAGES.c.source_chain_id == index.source_chain_id,
                LAYER_ZERO_MESSAGES.c.dest_chain_id == index.dest_chain_id,
                LAYER_ZERO_MESSAGES.c.nonce == index.message_id,
            )
        )

        result = await self.db.fetch_one(query)

        return LayerZeroMessageInDb(**result) if result else None

    async def retrieve_wormhole_message(
        self, index: WhCompositeIndex
    ) -> Optional[WormholeMessageInDb]:
        """Retrieves a Wormhole message."""

        query = WORMHOLE_MESSAGES.select().where(
            and_(
                WORMHOLE_MESSAGES.c.emitter_address == index.emitter_address,
                WORMHOLE_MESSAGES.c.source_chain_id == index.source_chain_id,
                WORMHOLE_MESSAGES.c.sequence == index.message_id,
            )
        )

        result = await self.db.fetch_one(query)

        return WormholeMessageInDb(**result) if result else None
