from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class ChainGovernorConfig(_message.Message):
    __slots__ = ["chains", "counter", "node_name", "timestamp", "tokens"]

    class Chain(_message.Message):
        __slots__ = ["big_transaction_size", "chain_id", "notional_limit"]
        BIG_TRANSACTION_SIZE_FIELD_NUMBER: _ClassVar[int]
        CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
        NOTIONAL_LIMIT_FIELD_NUMBER: _ClassVar[int]
        big_transaction_size: int
        chain_id: int
        notional_limit: int
        def __init__(
            self,
            chain_id: _Optional[int] = ...,
            notional_limit: _Optional[int] = ...,
            big_transaction_size: _Optional[int] = ...,
        ) -> None: ...

    class Token(_message.Message):
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
    CHAINS_FIELD_NUMBER: _ClassVar[int]
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    chains: _containers.RepeatedCompositeFieldContainer[ChainGovernorConfig.Chain]
    counter: int
    node_name: str
    timestamp: int
    tokens: _containers.RepeatedCompositeFieldContainer[ChainGovernorConfig.Token]
    def __init__(
        self,
        node_name: _Optional[str] = ...,
        counter: _Optional[int] = ...,
        timestamp: _Optional[int] = ...,
        chains: _Optional[_Iterable[_Union[ChainGovernorConfig.Chain, _Mapping]]] = ...,
        tokens: _Optional[_Iterable[_Union[ChainGovernorConfig.Token, _Mapping]]] = ...,
    ) -> None: ...

class ChainGovernorStatus(_message.Message):
    __slots__ = ["chains", "counter", "node_name", "timestamp"]

    class Chain(_message.Message):
        __slots__ = ["chain_id", "emitters", "remaining_available_notional"]
        CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
        EMITTERS_FIELD_NUMBER: _ClassVar[int]
        REMAINING_AVAILABLE_NOTIONAL_FIELD_NUMBER: _ClassVar[int]
        chain_id: int
        emitters: _containers.RepeatedCompositeFieldContainer[
            ChainGovernorStatus.Emitter
        ]
        remaining_available_notional: int
        def __init__(
            self,
            chain_id: _Optional[int] = ...,
            remaining_available_notional: _Optional[int] = ...,
            emitters: _Optional[
                _Iterable[_Union[ChainGovernorStatus.Emitter, _Mapping]]
            ] = ...,
        ) -> None: ...

    class Emitter(_message.Message):
        __slots__ = ["emitter_address", "enqueued_vaas", "total_enqueued_vaas"]
        EMITTER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        ENQUEUED_VAAS_FIELD_NUMBER: _ClassVar[int]
        TOTAL_ENQUEUED_VAAS_FIELD_NUMBER: _ClassVar[int]
        emitter_address: str
        enqueued_vaas: _containers.RepeatedCompositeFieldContainer[
            ChainGovernorStatus.EnqueuedVAA
        ]
        total_enqueued_vaas: int
        def __init__(
            self,
            emitter_address: _Optional[str] = ...,
            total_enqueued_vaas: _Optional[int] = ...,
            enqueued_vaas: _Optional[
                _Iterable[_Union[ChainGovernorStatus.EnqueuedVAA, _Mapping]]
            ] = ...,
        ) -> None: ...

    class EnqueuedVAA(_message.Message):
        __slots__ = ["notional_value", "release_time", "sequence", "tx_hash"]
        NOTIONAL_VALUE_FIELD_NUMBER: _ClassVar[int]
        RELEASE_TIME_FIELD_NUMBER: _ClassVar[int]
        SEQUENCE_FIELD_NUMBER: _ClassVar[int]
        TX_HASH_FIELD_NUMBER: _ClassVar[int]
        notional_value: int
        release_time: int
        sequence: int
        tx_hash: str
        def __init__(
            self,
            sequence: _Optional[int] = ...,
            release_time: _Optional[int] = ...,
            notional_value: _Optional[int] = ...,
            tx_hash: _Optional[str] = ...,
        ) -> None: ...
    CHAINS_FIELD_NUMBER: _ClassVar[int]
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    chains: _containers.RepeatedCompositeFieldContainer[ChainGovernorStatus.Chain]
    counter: int
    node_name: str
    timestamp: int
    def __init__(
        self,
        node_name: _Optional[str] = ...,
        counter: _Optional[int] = ...,
        timestamp: _Optional[int] = ...,
        chains: _Optional[_Iterable[_Union[ChainGovernorStatus.Chain, _Mapping]]] = ...,
    ) -> None: ...

class GossipMessage(_message.Message):
    __slots__ = [
        "signed_batch_observation",
        "signed_batch_vaa_with_quorum",
        "signed_chain_governor_config",
        "signed_chain_governor_status",
        "signed_heartbeat",
        "signed_observation",
        "signed_observation_request",
        "signed_vaa_with_quorum",
    ]
    SIGNED_BATCH_OBSERVATION_FIELD_NUMBER: _ClassVar[int]
    SIGNED_BATCH_VAA_WITH_QUORUM_FIELD_NUMBER: _ClassVar[int]
    SIGNED_CHAIN_GOVERNOR_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SIGNED_CHAIN_GOVERNOR_STATUS_FIELD_NUMBER: _ClassVar[int]
    SIGNED_HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    SIGNED_OBSERVATION_FIELD_NUMBER: _ClassVar[int]
    SIGNED_OBSERVATION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SIGNED_VAA_WITH_QUORUM_FIELD_NUMBER: _ClassVar[int]
    signed_batch_observation: SignedBatchObservation
    signed_batch_vaa_with_quorum: SignedBatchVAAWithQuorum
    signed_chain_governor_config: SignedChainGovernorConfig
    signed_chain_governor_status: SignedChainGovernorStatus
    signed_heartbeat: SignedHeartbeat
    signed_observation: SignedObservation
    signed_observation_request: SignedObservationRequest
    signed_vaa_with_quorum: SignedVAAWithQuorum
    def __init__(
        self,
        signed_observation: _Optional[_Union[SignedObservation, _Mapping]] = ...,
        signed_heartbeat: _Optional[_Union[SignedHeartbeat, _Mapping]] = ...,
        signed_vaa_with_quorum: _Optional[_Union[SignedVAAWithQuorum, _Mapping]] = ...,
        signed_observation_request: _Optional[
            _Union[SignedObservationRequest, _Mapping]
        ] = ...,
        signed_batch_observation: _Optional[
            _Union[SignedBatchObservation, _Mapping]
        ] = ...,
        signed_batch_vaa_with_quorum: _Optional[
            _Union[SignedBatchVAAWithQuorum, _Mapping]
        ] = ...,
        signed_chain_governor_config: _Optional[
            _Union[SignedChainGovernorConfig, _Mapping]
        ] = ...,
        signed_chain_governor_status: _Optional[
            _Union[SignedChainGovernorStatus, _Mapping]
        ] = ...,
    ) -> None: ...

class Heartbeat(_message.Message):
    __slots__ = [
        "boot_timestamp",
        "counter",
        "features",
        "guardian_addr",
        "networks",
        "node_name",
        "timestamp",
        "version",
    ]

    class Network(_message.Message):
        __slots__ = ["contract_address", "error_count", "height", "id"]
        CONTRACT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        ERROR_COUNT_FIELD_NUMBER: _ClassVar[int]
        HEIGHT_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        contract_address: str
        error_count: int
        height: int
        id: int
        def __init__(
            self,
            id: _Optional[int] = ...,
            height: _Optional[int] = ...,
            contract_address: _Optional[str] = ...,
            error_count: _Optional[int] = ...,
        ) -> None: ...
    BOOT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    GUARDIAN_ADDR_FIELD_NUMBER: _ClassVar[int]
    NETWORKS_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    boot_timestamp: int
    counter: int
    features: _containers.RepeatedScalarFieldContainer[str]
    guardian_addr: str
    networks: _containers.RepeatedCompositeFieldContainer[Heartbeat.Network]
    node_name: str
    timestamp: int
    version: str
    def __init__(
        self,
        node_name: _Optional[str] = ...,
        counter: _Optional[int] = ...,
        timestamp: _Optional[int] = ...,
        networks: _Optional[_Iterable[_Union[Heartbeat.Network, _Mapping]]] = ...,
        version: _Optional[str] = ...,
        guardian_addr: _Optional[str] = ...,
        boot_timestamp: _Optional[int] = ...,
        features: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class ObservationRequest(_message.Message):
    __slots__ = ["chain_id", "tx_hash"]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    chain_id: int
    tx_hash: bytes
    def __init__(
        self, chain_id: _Optional[int] = ..., tx_hash: _Optional[bytes] = ...
    ) -> None: ...

class SignedBatchObservation(_message.Message):
    __slots__ = ["addr", "batch_id", "chain_id", "hash", "nonce", "signature", "tx_id"]
    ADDR_FIELD_NUMBER: _ClassVar[int]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    TX_ID_FIELD_NUMBER: _ClassVar[int]
    addr: bytes
    batch_id: str
    chain_id: int
    hash: bytes
    nonce: int
    signature: bytes
    tx_id: bytes
    def __init__(
        self,
        addr: _Optional[bytes] = ...,
        hash: _Optional[bytes] = ...,
        signature: _Optional[bytes] = ...,
        tx_id: _Optional[bytes] = ...,
        chain_id: _Optional[int] = ...,
        nonce: _Optional[int] = ...,
        batch_id: _Optional[str] = ...,
    ) -> None: ...

class SignedBatchVAAWithQuorum(_message.Message):
    __slots__ = ["batch_id", "batch_vaa", "chain_id", "nonce", "tx_id"]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    BATCH_VAA_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    TX_ID_FIELD_NUMBER: _ClassVar[int]
    batch_id: str
    batch_vaa: bytes
    chain_id: int
    nonce: int
    tx_id: bytes
    def __init__(
        self,
        batch_vaa: _Optional[bytes] = ...,
        chain_id: _Optional[int] = ...,
        tx_id: _Optional[bytes] = ...,
        nonce: _Optional[int] = ...,
        batch_id: _Optional[str] = ...,
    ) -> None: ...

class SignedChainGovernorConfig(_message.Message):
    __slots__ = ["config", "guardian_addr", "signature"]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    GUARDIAN_ADDR_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    config: bytes
    guardian_addr: bytes
    signature: bytes
    def __init__(
        self,
        config: _Optional[bytes] = ...,
        signature: _Optional[bytes] = ...,
        guardian_addr: _Optional[bytes] = ...,
    ) -> None: ...

class SignedChainGovernorStatus(_message.Message):
    __slots__ = ["guardian_addr", "signature", "status"]
    GUARDIAN_ADDR_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    guardian_addr: bytes
    signature: bytes
    status: bytes
    def __init__(
        self,
        status: _Optional[bytes] = ...,
        signature: _Optional[bytes] = ...,
        guardian_addr: _Optional[bytes] = ...,
    ) -> None: ...

class SignedHeartbeat(_message.Message):
    __slots__ = ["guardian_addr", "heartbeat", "signature"]
    GUARDIAN_ADDR_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    guardian_addr: bytes
    heartbeat: bytes
    signature: bytes
    def __init__(
        self,
        heartbeat: _Optional[bytes] = ...,
        signature: _Optional[bytes] = ...,
        guardian_addr: _Optional[bytes] = ...,
    ) -> None: ...

class SignedObservation(_message.Message):
    __slots__ = ["addr", "hash", "message_id", "signature", "tx_hash"]
    ADDR_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    addr: bytes
    hash: bytes
    message_id: str
    signature: bytes
    tx_hash: bytes
    def __init__(
        self,
        addr: _Optional[bytes] = ...,
        hash: _Optional[bytes] = ...,
        signature: _Optional[bytes] = ...,
        tx_hash: _Optional[bytes] = ...,
        message_id: _Optional[str] = ...,
    ) -> None: ...

class SignedObservationRequest(_message.Message):
    __slots__ = ["guardian_addr", "observation_request", "signature"]
    GUARDIAN_ADDR_FIELD_NUMBER: _ClassVar[int]
    OBSERVATION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    guardian_addr: bytes
    observation_request: bytes
    signature: bytes
    def __init__(
        self,
        observation_request: _Optional[bytes] = ...,
        signature: _Optional[bytes] = ...,
        guardian_addr: _Optional[bytes] = ...,
    ) -> None: ...

class SignedVAAWithQuorum(_message.Message):
    __slots__ = ["vaa"]
    VAA_FIELD_NUMBER: _ClassVar[int]
    vaa: bytes
    def __init__(self, vaa: _Optional[bytes] = ...) -> None: ...
