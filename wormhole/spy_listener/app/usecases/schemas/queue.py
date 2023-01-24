from pydantic import BaseModel, Field


class QueueException(Exception):
    """Errors rasised when interacting with RabbitMQ."""

    detail: str


class QueueError(QueueException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.detail = kwargs.get("detail")


class QueueMessage(BaseModel):
    """Message sent to queue."""

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
    vaa_hex: str = Field(
        ...,
        description="The VAA represented in hexadecimal format.",
        example="0E31Cc997F3C3bBD3091449eF03DAB3b7455A02D",
    )
