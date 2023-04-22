from enum import Enum

from app.usecases.interfaces.clients.unique_set import IUniqueSetClient
from app.usecases.schemas.unique_set import UniqueSetError, UniqueSetMessage
from tests import constants as constant


class UniqueSetResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class MockUniqueSetClient(IUniqueSetClient):
    def __init__(self, result: UniqueSetResult) -> None:
        self.result = result

    async def publish(self, message: UniqueSetMessage) -> None:
        """Publishes message to unique set."""
        if self.result == UniqueSetResult.SUCCESS:
            return 1
        raise UniqueSetError(detail=constant.UNIQUE_SET_ERROR_DETAIL)

    async def close_connection(self) -> None:
        return
