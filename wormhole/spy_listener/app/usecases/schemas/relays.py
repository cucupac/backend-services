from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Status(str, Enum):
    PENDING = "pending"
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
        ..., description="The status of the relay.", example=Status.PENDING
    )
    error: Optional[str] = Field(
        None,
        description="Error pertaining to relay.",
        example="An error happend, and here's why.",
    )
    from_cache: Optional[bool] = Field(
        None,
        description="Whether or not the message was ever cached.",
        example=False,
    )
