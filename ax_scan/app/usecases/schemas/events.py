from enum import Enum

from pydantic import BaseModel

from app.settings import settings


class EmitterAddress(str, Enum):
    """Possible emitter addresses."""

    WORMHOLE_BRIDGE = settings.evm_wormhole_bridge
    LAYER_ZERO_BRIDGE = settings.evm_layerzero_bridge
    TREASURY = settings.treasury


class EvmEvent(BaseModel):
    emitter_address: str
    block_number: int
    block_hash: str
    transaction_hash: str


class CrossChainEvent(EvmEvent):
    source_chain_id: int
    dest_chain_id: int
    amount: int
    message_id: int


class SendToChain(CrossChainEvent):
    """Event emitted on source chains."""

    from_address: str


class ReceiveFromChain(CrossChainEvent):
    """Event emitted on destination chains."""

    to_address: str


class Mint(EvmEvent):
    """Event emitted on Treasury contract when USX is minted."""

    account: str
    amount: int


class BlockRange(BaseModel):
    """The range of blocks to query events for."""

    from_block: int
    to_block: int
