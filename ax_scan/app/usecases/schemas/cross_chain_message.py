from datetime import datetime

from pydantic import BaseModel


class LzCompositeIndex(BaseModel):
    """A composite index in the layer_zero_messages database table."""

    emitter_address: str
    source_chain_id: int
    dest_chain_id: int
    message_id: int


class WhCompositeIndex(BaseModel):
    """A composite index in the layer_zero_messages database table."""

    emitter_address: str
    source_chain_id: int
    message_id: int


class LzMessage(LzCompositeIndex):
    """A LayerZero Message."""


class WhMessage(WhCompositeIndex):
    """A Wormhole Message."""


class LayerZeroMessageInDb(LzMessage):
    id: int
    created_at: datetime
    updated_at: datetime


class WormholeMessageInDb(WhMessage):
    id: int
    created_at: datetime
    updated_at: datetime
