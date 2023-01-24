from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers
from gossip.v1 import gossip_pb2 as _gossip_pb2
from publicrpc.v1 import publicrpc_pb2 as _publicrpc_pb2

DESCRIPTOR: _descriptor.FileDescriptor

class BatchFilter(_message.Message):
    __slots__ = ["chain_id", "nonce", "tx_id"]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    TX_ID_FIELD_NUMBER: _ClassVar[int]
    chain_id: _publicrpc_pb2.ChainID
    nonce: int
    tx_id: bytes
    def __init__(
        self,
        chain_id: _Optional[_Union[_publicrpc_pb2.ChainID, str]] = ...,
        tx_id: _Optional[bytes] = ...,
        nonce: _Optional[int] = ...,
    ) -> None: ...

class BatchTransactionFilter(_message.Message):
    __slots__ = ["chain_id", "tx_id"]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    TX_ID_FIELD_NUMBER: _ClassVar[int]
    chain_id: _publicrpc_pb2.ChainID
    tx_id: bytes
    def __init__(
        self,
        chain_id: _Optional[_Union[_publicrpc_pb2.ChainID, str]] = ...,
        tx_id: _Optional[bytes] = ...,
    ) -> None: ...

class EmitterFilter(_message.Message):
    __slots__ = ["chain_id", "emitter_address"]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    EMITTER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    chain_id: _publicrpc_pb2.ChainID
    emitter_address: str
    def __init__(
        self,
        chain_id: _Optional[_Union[_publicrpc_pb2.ChainID, str]] = ...,
        emitter_address: _Optional[str] = ...,
    ) -> None: ...

class FilterEntry(_message.Message):
    __slots__ = ["batch_filter", "batch_transaction_filter", "emitter_filter"]
    BATCH_FILTER_FIELD_NUMBER: _ClassVar[int]
    BATCH_TRANSACTION_FILTER_FIELD_NUMBER: _ClassVar[int]
    EMITTER_FILTER_FIELD_NUMBER: _ClassVar[int]
    batch_filter: BatchFilter
    batch_transaction_filter: BatchTransactionFilter
    emitter_filter: EmitterFilter
    def __init__(
        self,
        emitter_filter: _Optional[_Union[EmitterFilter, _Mapping]] = ...,
        batch_filter: _Optional[_Union[BatchFilter, _Mapping]] = ...,
        batch_transaction_filter: _Optional[
            _Union[BatchTransactionFilter, _Mapping]
        ] = ...,
    ) -> None: ...

class SubscribeSignedVAAByTypeRequest(_message.Message):
    __slots__ = ["filters"]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.RepeatedCompositeFieldContainer[FilterEntry]
    def __init__(
        self, filters: _Optional[_Iterable[_Union[FilterEntry, _Mapping]]] = ...
    ) -> None: ...

class SubscribeSignedVAAByTypeResponse(_message.Message):
    __slots__ = ["signed_batch_vaa", "signed_vaa"]
    SIGNED_BATCH_VAA_FIELD_NUMBER: _ClassVar[int]
    SIGNED_VAA_FIELD_NUMBER: _ClassVar[int]
    signed_batch_vaa: _gossip_pb2.SignedBatchVAAWithQuorum
    signed_vaa: _gossip_pb2.SignedVAAWithQuorum
    def __init__(
        self,
        signed_vaa: _Optional[_Union[_gossip_pb2.SignedVAAWithQuorum, _Mapping]] = ...,
        signed_batch_vaa: _Optional[
            _Union[_gossip_pb2.SignedBatchVAAWithQuorum, _Mapping]
        ] = ...,
    ) -> None: ...

class SubscribeSignedVAARequest(_message.Message):
    __slots__ = ["filters"]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.RepeatedCompositeFieldContainer[FilterEntry]
    def __init__(
        self, filters: _Optional[_Iterable[_Union[FilterEntry, _Mapping]]] = ...
    ) -> None: ...

class SubscribeSignedVAAResponse(_message.Message):
    __slots__ = ["vaa_bytes"]
    VAA_BYTES_FIELD_NUMBER: _ClassVar[int]
    vaa_bytes: bytes
    def __init__(self, vaa_bytes: _Optional[bytes] = ...) -> None: ...
