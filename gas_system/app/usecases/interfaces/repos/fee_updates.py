from abc import ABC, abstractmethod

from app.usecases.schemas.fees import FeeUpdate


class IFeeUpdateRepo(ABC):
    @abstractmethod
    async def create(self, fee_update: FeeUpdate) -> None:
        """Inserts and returns new fee update object."""
