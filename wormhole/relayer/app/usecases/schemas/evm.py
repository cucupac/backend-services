from hexbytes import HexBytes


class TransactionHash(HexBytes):
    """EVM transaction hash."""


class EvmClientException(Exception):
    """Errors rasised when interacting with EVM nodes."""

    detail: str


class EvmClientError(EvmClientException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.detail = kwargs.get("detail")
