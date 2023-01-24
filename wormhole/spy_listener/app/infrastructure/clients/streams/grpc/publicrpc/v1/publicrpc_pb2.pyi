from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from gossip.v1 import gossip_pb2 as _gossip_pb2

CHAIN_ID_ACALA: ChainID
CHAIN_ID_ALGORAND: ChainID
CHAIN_ID_APTOS: ChainID
CHAIN_ID_ARBITRUM: ChainID
CHAIN_ID_AURORA: ChainID
CHAIN_ID_AVALANCHE: ChainID
CHAIN_ID_BSC: ChainID
CHAIN_ID_BTC: ChainID
CHAIN_ID_CELO: ChainID
CHAIN_ID_ETHEREUM: ChainID
CHAIN_ID_FANTOM: ChainID
CHAIN_ID_GNOSIS: ChainID
CHAIN_ID_INJECTIVE: ChainID
CHAIN_ID_KARURA: ChainID
CHAIN_ID_KLAYTN: ChainID
CHAIN_ID_MOONBEAM: ChainID
CHAIN_ID_NEAR: ChainID
CHAIN_ID_NEON: ChainID
CHAIN_ID_OASIS: ChainID
CHAIN_ID_OPTIMISM: ChainID
CHAIN_ID_OSMOSIS: ChainID
CHAIN_ID_POLYGON: ChainID
CHAIN_ID_PYTHNET: ChainID
CHAIN_ID_SOLANA: ChainID
CHAIN_ID_SUI: ChainID
CHAIN_ID_TERRA: ChainID
CHAIN_ID_TERRA2: ChainID
CHAIN_ID_UNSPECIFIED: ChainID
CHAIN_ID_XPLA: ChainID
DESCRIPTOR: _descriptor.FileDescriptor

class BatchID(_message.Message):
    __slots__ = ["emitter_chain", "nonce", "tx_id"]
    EMITTER_CHAIN_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    TX_ID_FIELD_NUMBER: _ClassVar[int]
    emitter_chain: ChainID
    nonce: int
    tx_id: bytes
    def __init__(
        self,
        emitter_chain: _Optional[_Union[ChainID, str]] = ...,
        tx_id: _Optional[bytes] = ...,
        nonce: _Optional[int] = ...,
    ) -> None: ...

class GetCurrentGuardianSetRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetCurrentGuardianSetResponse(_message.Message):
    __slots__ = ["guardian_set"]
    GUARDIAN_SET_FIELD_NUMBER: _ClassVar[int]
    guardian_set: GuardianSet
    def __init__(
        self, guardian_set: _Optional[_Union[GuardianSet, _Mapping]] = ...
    ) -> None: ...

class GetLastHeartbeatsRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetLastHeartbeatsResponse(_message.Message):
    __slots__ = ["entries"]

    class Entry(_message.Message):
        __slots__ = ["p2p_node_addr", "raw_heartbeat", "verified_guardian_addr"]
        P2P_NODE_ADDR_FIELD_NUMBER: _ClassVar[int]
        RAW_HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
        VERIFIED_GUARDIAN_ADDR_FIELD_NUMBER: _ClassVar[int]
        p2p_node_addr: str
        raw_heartbeat: _gossip_pb2.Heartbeat
        verified_guardian_addr: str
        def __init__(
            self,
            verified_guardian_addr: _Optional[str] = ...,
            p2p_node_addr: _Optional[str] = ...,
            raw_heartbeat: _Optional[_Union[_gossip_pb2.Heartbeat, _Mapping]] = ...,
        ) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[
        GetLastHeartbeatsResponse.Entry
    ]
    def __init__(
        self,
        entries: _Optional[
            _Iterable[_Union[GetLastHeartbeatsResponse.Entry, _Mapping]]
        ] = ...,
    ) -> None: ...

class GetSignedBatchVAARequest(_message.Message):
    __slots__ = ["batch_id"]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    batch_id: BatchID
    def __init__(
        self, batch_id: _Optional[_Union[BatchID, _Mapping]] = ...
    ) -> None: ...

class GetSignedBatchVAAResponse(_message.Message):
    __slots__ = ["signed_batch_vaa"]
    SIGNED_BATCH_VAA_FIELD_NUMBER: _ClassVar[int]
    signed_batch_vaa: _gossip_pb2.SignedBatchVAAWithQuorum
    def __init__(
        self,
        signed_batch_vaa: _Optional[
            _Union[_gossip_pb2.SignedBatchVAAWithQuorum, _Mapping]
        ] = ...,
    ) -> None: ...

class GetSignedVAARequest(_message.Message):
    __slots__ = ["message_id"]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    message_id: MessageID
    def __init__(
        self, message_id: _Optional[_Union[MessageID, _Mapping]] = ...
    ) -> None: ...

class GetSignedVAAResponse(_message.Message):
    __slots__ = ["vaa_bytes"]
    VAA_BYTES_FIELD_NUMBER: _ClassVar[int]
    vaa_bytes: bytes
    def __init__(self, vaa_bytes: _Optional[bytes] = ...) -> None: ...

class GovernorGetAvailableNotionalByChainRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GovernorGetAvailableNotionalByChainResponse(_message.Message):
    __slots__ = ["entries"]

    class Entry(_message.Message):
        __slots__ = [
            "big_transaction_size",
            "chain_id",
            "notional_limit",
            "remaining_available_notional",
        ]
        BIG_TRANSACTION_SIZE_FIELD_NUMBER: _ClassVar[int]
        CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
        NOTIONAL_LIMIT_FIELD_NUMBER: _ClassVar[int]
        REMAINING_AVAILABLE_NOTIONAL_FIELD_NUMBER: _ClassVar[int]
        big_transaction_size: int
        chain_id: int
        notional_limit: int
        remaining_available_notional: int
        def __init__(
            self,
            chain_id: _Optional[int] = ...,
            remaining_available_notional: _Optional[int] = ...,
            notional_limit: _Optional[int] = ...,
            big_transaction_size: _Optional[int] = ...,
        ) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[
        GovernorGetAvailableNotionalByChainResponse.Entry
    ]
    def __init__(
        self,
        entries: _Optional[
            _Iterable[
                _Union[GovernorGetAvailableNotionalByChainResponse.Entry, _Mapping]
            ]
        ] = ...,
    ) -> None: ...

class GovernorGetEnqueuedVAAsRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GovernorGetEnqueuedVAAsResponse(_message.Message):
    __slots__ = ["entries"]

    class Entry(_message.Message):
        __slots__ = [
            "emitter_address",
            "emitter_chain",
            "notional_value",
            "release_time",
            "sequence",
            "tx_hash",
        ]
        EMITTER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        EMITTER_CHAIN_FIELD_NUMBER: _ClassVar[int]
        NOTIONAL_VALUE_FIELD_NUMBER: _ClassVar[int]
        RELEASE_TIME_FIELD_NUMBER: _ClassVar[int]
        SEQUENCE_FIELD_NUMBER: _ClassVar[int]
        TX_HASH_FIELD_NUMBER: _ClassVar[int]
        emitter_address: str
        emitter_chain: int
        notional_value: int
        release_time: int
        sequence: int
        tx_hash: str
        def __init__(
            self,
            emitter_chain: _Optional[int] = ...,
            emitter_address: _Optional[str] = ...,
            sequence: _Optional[int] = ...,
            release_time: _Optional[int] = ...,
            notional_value: _Optional[int] = ...,
            tx_hash: _Optional[str] = ...,
        ) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[
        GovernorGetEnqueuedVAAsResponse.Entry
    ]
    def __init__(
        self,
        entries: _Optional[
            _Iterable[_Union[GovernorGetEnqueuedVAAsResponse.Entry, _Mapping]]
        ] = ...,
    ) -> None: ...

class GovernorGetTokenListRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GovernorGetTokenListResponse(_message.Message):
    __slots__ = ["entries"]

    class Entry(_message.Message):
        __slots__ = ["origin_address", "origin_chain_id", "price"]
        ORIGIN_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        ORIGIN_CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        origin_address: str
        origin_chain_id: int
        price: float
        def __init__(
            self,
            origin_chain_id: _Optional[int] = ...,
            origin_address: _Optional[str] = ...,
            price: _Optional[float] = ...,
        ) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[
        GovernorGetTokenListResponse.Entry
    ]
    def __init__(
        self,
        entries: _Optional[
            _Iterable[_Union[GovernorGetTokenListResponse.Entry, _Mapping]]
        ] = ...,
    ) -> None: ...

class GovernorIsVAAEnqueuedRequest(_message.Message):
    __slots__ = ["message_id"]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    message_id: MessageID
    def __init__(
        self, message_id: _Optional[_Union[MessageID, _Mapping]] = ...
    ) -> None: ...

class GovernorIsVAAEnqueuedResponse(_message.Message):
    __slots__ = ["is_enqueued"]
    IS_ENQUEUED_FIELD_NUMBER: _ClassVar[int]
    is_enqueued: bool
    def __init__(self, is_enqueued: bool = ...) -> None: ...

class GuardianSet(_message.Message):
    __slots__ = ["addresses", "index"]
    ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    addresses: _containers.RepeatedScalarFieldContainer[str]
    index: int
    def __init__(
        self, index: _Optional[int] = ..., addresses: _Optional[_Iterable[str]] = ...
    ) -> None: ...

class MessageID(_message.Message):
    __slots__ = ["emitter_address", "emitter_chain", "sequence"]
    EMITTER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    EMITTER_CHAIN_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    emitter_address: str
    emitter_chain: ChainID
    sequence: int
    def __init__(
        self,
        emitter_chain: _Optional[_Union[ChainID, str]] = ...,
        emitter_address: _Optional[str] = ...,
        sequence: _Optional[int] = ...,
    ) -> None: ...

class ChainID(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
