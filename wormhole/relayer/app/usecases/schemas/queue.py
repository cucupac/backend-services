from pydantic import BaseModel, Field


class QueueException(Exception):
    """Errors rasised when interacting with RabbitMQ."""

    detail: str


class QueueError(QueueException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.detail = kwargs.get("detail")


class QueueMessage(BaseModel):
    """Message received from queue."""

    dest_chain_id: int = (
        Field(
            ..., description="The Wormhole-ascribed destination-chain ID.", example=5
        ),
    )
    to_address: str = Field(
        ...,
        description="The account address of the recipient.",
        example="0xE37c0D48d3F0D7E9b2b5E29c5D5b2c7B9fE37c0D",
    )
    sequence: int = Field(
        ...,
        description="The emitter contract's chronological sequence of the cross-chain message.",
        example=1,
    )
    emitter_chain: int = Field(
        ...,
        description="The Wormhole-ascribed source-chain ID.",
        example=5,
    )
    emitter_address: str = Field(
        ...,
        description="The address of the contract on the source-chain that emitted the cross-chain message.",
        example="0xbf8a1387d4682b5b431cea8f53edd5e7a7834861",
    )
    vaa_hex: str = Field(
        ...,
        description="The VAA represented in hexadecimal format.",
        example="0E31Cc997F3C3bBD3091449eF03DAB3b7455A02D",
    )
