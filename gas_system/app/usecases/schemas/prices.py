from pydantic import BaseModel


class PriceClientException(Exception):
    """Errors raised when interacting with a price client."""

    detail: str


class PriceClientError(PriceClientException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.detail = kwargs.get("detail")


class APIErrorBody(BaseModel):
    detail: str
