from abc import ABC, abstractmethod

from app.usecases.schemas.relays import UpdateRepoAdapter


class IRelaysRepo(ABC):
    @abstractmethod
    async def update(self, relay: UpdateRepoAdapter) -> None:
        """Update relay object."""
