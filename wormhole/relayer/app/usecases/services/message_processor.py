import hashlib
import struct

from eth_abi import decode

from app.usecases.interfaces.services.message_processor import IVaaProcessor
from app.usecases.schemas.vaa import ParsedPayload, ParsedVaa


class MessageProcessor(IVaaProcessor):
    def __init__(self):
        pass

    def parse_vaa(self, vaa: bytes) -> ParsedVaa:
        """Extracts utilizable data from VAA bytes."""

        sig_start = 6
        number_of_signers = vaa[5]
        sig_length = 66

        guardian_signatures = []
        for i in range(number_of_signers):
            start = sig_start + i * sig_length
            guardian_signatures.append(
                {
                    "index": vaa[start],
                    "signature": vaa[start + 1 : start + 66],
                }
            )

        body = vaa[sig_start + sig_length * number_of_signers :]

        return ParsedVaa(
            version=vaa[0],
            guardian_set_index=struct.unpack(">I", vaa[1:5])[0],
            guardian_signatures=guardian_signatures,
            timestamp=struct.unpack(">I", body[:4])[0],
            nonce=struct.unpack(">I", body[4:8])[0],
            emitter_chain=struct.unpack(">H", body[8:10])[0],
            emitter_address="0x" + hex(int(body[10:42].hex(), 16))[2:],
            sequence=int.from_bytes(body[42:50], byteorder="big", signed=False),
            consistency_level=body[50],
            payload=self.parse_payload(payload=body[51:]),
            hash=hashlib.sha3_256(body).digest(),
        )

    def parse_payload(self, payload: bytes) -> ParsedPayload:
        """Extracts utilizable data from payload bytes."""

        types = ["bytes", "uint256", "uint256", "uint256"]
        from_address_bytes, dest_chain_id, to_address_uint256, amount = decode(
            types, payload
        )

        return ParsedPayload(
            from_address="0x" + str(from_address_bytes.hex()),
            to_address=to_address_uint256,
            dest_chain_id=dest_chain_id,
            amount=amount,
        )
