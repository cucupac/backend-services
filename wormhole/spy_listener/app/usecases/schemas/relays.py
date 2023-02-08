from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Status(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


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
    sequence: Optional[int] = Field(
        None,
        description="The bridging-protocol-assigned sequence of the transaction.",
        example=1,
    )
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
