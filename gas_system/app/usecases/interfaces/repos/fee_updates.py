from abc import ABC, abstractmethod

from app.usecases.schemas.fees import FeeUpdate, FeeUpdateInDb


class IFeeUpdatesRepo(ABC):
    @abstractmethod
    async def create(self, fee_update: FeeUpdate) -> None:
        """Inserts and returns new fee update object."""

    @abstractmethod
    async def retrieve(self, fee_update_id: int) -> FeeUpdateInDb:
        """Retrieves a fee update object."""

    @abstractmethod
    async def retrieve_last_update_by_chain_id(self, chain_id: int) -> FeeUpdateInDb:
        """Retrieves the last recorded feel update by chain ID."""
