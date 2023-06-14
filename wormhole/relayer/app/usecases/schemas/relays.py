# pylint: disable=duplicate-code
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Status(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class CacheStatus(str, Enum):
    NEVER_CACHED = "never_cached"
    CURRENTLY_CACHED = "currently_cached"
    PREVIOUSLY_CACHED = "previously_cached"


class GrpcStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class RelayErrors(str, Enum):
    MISSED_VAA = "[gRPC Stream]: Missed VAA."
    STALE_PENDING = "[General]: Message was pending for longer than a minute."


class UpdateRepoAdapter(BaseModel):
    emitter_address: str = Field(
        ...,
        description="The bridge contract address used to faciliate the cross-chain transaction.",
        example="0xd99E99239D6F14372E994c15e60A039D88c9d16A",
    )
    source_chain_id: int = Field(
        ...,
        description="The source chain's bridging-protocol-assigned chain ID.",
        example=5,
    )
    sequence: int = Field(
        ...,
        description="The bridging-protocol-assigned sequence of the transaction.",
        example=1,
    )
    status: Optional[Status] = Field(
        None, description="The status of the relay.", example=Status.SUCCESS
    )
    transaction_hash: Optional[str] = Field(
        None,
        description="The hash of the submitted transaction.",
        example="0xb5c8bd9430b6cc87a0e2fe110ece6bf527fa4f170a4bc8cd032f768fc5219838",
    )
    error: Optional[str] = Field(
        None,
        description="Error pertaining to relay.",
        example="An error happend, and here's why.",
    )


class UpdateJoinedRepoAdapter(UpdateRepoAdapter):
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
    message: Optional[str] = Field(
        None,
        description="The message that the consuming-relayer needs.",
        example="0CeC041cDB3AAB968C1a273bfC330aa410b5E2DF0CeC041cDB3AAB968C1a273bfC330aa410b5E2DF",
    )


class SubmittedRelay(BaseModel):
    status: Status = Field(
        ..., description="The status of the relay.", example=Status.SUCCESS
    )
    transaction_hash: Optional[str] = Field(
        None,
        description="The hash of the submitted transaction.",
        example="0xb5c8bd9430b6cc87a0e2fe110ece6bf527fa4f170a4bc8cd032f768fc5219838",
    )
    error: Optional[str] = Field(
        None,
        description="Error pertaining to relay.",
        example="An error happend, and here's why.",
    )
