from datetime import datetime

from pydantic import BaseModel


class LzCompositeIndex(BaseModel):
    """A composite index in the layer_zero_messages database table."""

    emitter_address: str
    source_chain_id: int
    dest_chain_id: int
    nonce: int


class WhCompositeIndex(BaseModel):
    """A composite index in the layer_zero_messages database table."""

    emitter_address: str
    source_chain_id: int
    sequence: int


class LzMessage(LzCompositeIndex):
    """A LayerZero Message."""


class WhMessage(WhCompositeIndex):
    """A Wormhole Message."""


class LayerZeroMessageInDb(LzMessage):
    id: int
    cross_chain_tx_id: int
    created_at: datetime
    updated_at: datetime


class WormholeMessageInDb(WhMessage):
    id: int
    cross_chain_tx_id: int
    created_at: datetime
    updated_at: datetime
