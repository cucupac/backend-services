from pydantic import BaseModel


class BridgeClientException(Exception):
    """Errors raised when interacting with a bridge client."""

    detail: str


class BridgeClientError(BridgeClientException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.detail = kwargs.get("detail")


class APIErrorBody(BaseModel):
    detail: str


class BridgeMessage(BaseModel):
    b64_message: str  # base64 encoded bytes


class NotFoundException(BridgeClientException):
    """Raised when a 404 is returned from the bridge client."""
