from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas.mints import MintData, MintInDb


class IMintsRepo(ABC):
    @abstractmethod
    async def create(self, tx_id: int, mint_data: MintData) -> Optional[int]:
        """Inserts a mint; returns mints id."""

    @abstractmethod
    async def retrieve_all_recent_mints(
        self,
    ) -> List[MintInDb]:
        """Retrieves total recent mints; returns a list of database mints."""
