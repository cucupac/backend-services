from abc import ABC, abstractmethod

from app.usecases.schemas.fees import FeeUpdate, FeeUpdateInDb


class IFeeUpdateRepo(ABC):
    @abstractmethod
    async def create(self, fee_update: FeeUpdate) -> None:
        """Inserts and returns new fee update object."""

    @abstractmethod
    async def retrieve(self, fee_update_id: int) -> FeeUpdateInDb:
        """Retrieves a fee update object."""
