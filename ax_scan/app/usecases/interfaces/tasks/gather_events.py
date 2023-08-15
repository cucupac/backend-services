from abc import ABC, abstractmethod
from typing import List

from app.usecases.schemas.events import BlockRange


class IGatherEventsTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts task."""

    @abstractmethod
    async def task(self, task_id: int) -> None:
        """Gathers untracked transactions."""

    @abstractmethod
    async def get_block_range(self, ax_chain_id: int) -> List[BlockRange]:
        """Returns a list of starting and ending blocks for a given chain's data query."""
