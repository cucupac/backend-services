from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Status(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    TESTING = "testing"


class CacheStatus(str, Enum):
    NEVER_CACHED = "never_cached"
    CURRENTLY_CACHED = "currently_cached"
    PREVIOUSLY_CACHED = "previously_cached"


class GrpcStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class TransactionBase(BaseModel):
    emitter_address: str = Field(
        ...,
        description="The bridge contract address used to faciliate the cross-chain transaction.",
        example="0xd99E99239D6F14372E994c15e60A039D88c9d16A",
    )
    from_address: Optional[str] = Field(
        None,
        description="The transaction's sender address.",
        example="0x0CeC041cDB3AAB968C1a273bfC330aa410b5E2DF",
    )
    to_address: Optional[str] = Field(
        None,
        description="The transaction's recipient address.",
        example="0x0CeC041cDB3AAB968C1a273bfC330aa410b5E2DF",
    )
    source_chain_id: int = Field(
        ...,
        description="The source chain's bridging-protocol-assigned chain ID.",
        example=5,
    )
    dest_chain_id: Optional[int] = Field(
        None,
        description="The destination chain's bridging-protocol-assigned chain ID.",
        example=2,
    )
    amount: Optional[int] = Field(
        None,
        description="The amount of USX transferred.",
        example=1e18,
    )
    sequence: int = Field(
        ...,
        description="The bridging-protocol-assigned sequence of the transaction.",
        example=1,
    )


class TransactionInDB(TransactionBase):
    """Database Object."""

    id: int = Field(
        ...,
        description="The unique identifier and primary key for the transactions table.",
        example=1,
    )
    created_at: datetime = Field(
        ...,
        description="The time that the transaction object was created.",
        example="2020-02-11 17:47:44.170522",
    )
    updated_at: datetime = Field(
        ...,
        description="The time that the transaction object was updated.",
        example="2020-02-11 17:47:44.170522",
    )


class TransactionsJoinRelays(TransactionInDB):
    relay_id: int = Field(
        ...,
        description="The unique identifier and primary key for the relays table.",
        example=1,
    )
    relay_status: Status = Field(
        ...,
        description="The relay status.",
        example="success",
    )
    relay_error: str = Field(
        None,
        description="Error pertaining to relay.",
        example="Some error.",
    )
    relay_message: Optional[str] = Field(
        None,
        description="The message that the consuming-relayer needs.",
        example="0CeC041cDB3AAB968C1a273bfC330aa410b5E2DF0CeC041cDB3AAB968C1a273bfC330aa410b5E2DF",
    )
    relay_transaction_hash: Optional[str] = Field(
        None,
        description="The hash of the submitted transaction.",
        example="0xb5c8bd9430b6cc87a0e2fe110ece6bf527fa4f170a4bc8cd032f768fc5219838",
    )
    relay_cache_status: CacheStatus = Field(
        ...,
        description="Informaiton on the relationship between the relay and the in-memory cache.",
        example=CacheStatus.NEVER_CACHED,
    )
    relay_grpc_status: GrpcStatus = Field(
        ...,
        description="Whether or not the gRPC stream failed.",
        example=GrpcStatus.SUCCESS,
    )
