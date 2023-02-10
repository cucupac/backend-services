from abc import ABC, abstractmethod

from app.usecases.schemas.vaa import ParsedPayload, ParsedVaa


class IVaaManager(ABC):
    @abstractmethod
    def process(self, vaa: bytes) -> None:
        """Processes vaa bytes."""

    @abstractmethod
    def parse_vaa(self, vaa: bytes) -> ParsedVaa:
        """Extracts utilizable data from VAA bytes."""

    @abstractmethod
    def parse_payload(self, payload: bytes) -> ParsedPayload:
        """Extracts utilizable data from payload bytes."""
