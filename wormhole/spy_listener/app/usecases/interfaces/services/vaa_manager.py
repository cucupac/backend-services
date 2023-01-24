from abc import ABC, abstractmethod

from app.usecases.schemas.vaa import ParsedPayload, ParsedVaa


class IVaaManager(ABC):
    @abstractmethod
    def process(self, vaa: bytes) -> None:
        """Processes vaa bytes."""

    @abstractmethod
    def _parse_vaa(self, vaa: bytes) -> ParsedVaa:
        """Extracts utilizable data from VAA bytes."""

    @abstractmethod
    def _parse_payload(self, payload: bytes) -> ParsedPayload:
        """Extracts utilizable data from payload bytes."""
