import codecs
import hashlib
import struct
from logging import Logger
from typing import Mapping

from eth_abi import decode_abi

from app.usecases.interfaces.clients.unique_set import IUniqueSetClient
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.services.vaa_manager import IVaaManager
from app.usecases.schemas.relays import CacheStatus, Status
from app.usecases.schemas.transactions import CreateRepoAdapter
from app.usecases.schemas.unique_set import UniqueSetException, UniqueSetMessage
from app.usecases.schemas.vaa import ParsedPayload, ParsedVaa


class VaaManager(IVaaManager):
    def __init__(
        self,
        transactions_repo: ITransactionsRepo,
        unique_set: IUniqueSetClient,
        logger: Logger,
    ):
        self.transactions_repo: ITransactionsRepo = transactions_repo
        self.unique_set: IUniqueSetClient = unique_set
        self.logger = logger
        self.recent_vaas: Mapping[frozenset, bool] = dict()

    async def process(self, vaa: bytes) -> None:
        """Process vaa bytes."""

        parsed_vaa = self.parse_vaa(vaa=vaa)

        vaa_hex = codecs.encode(bytes(vaa), "hex_codec").decode().upper()

        vaa_unique_set = frozenset(
            {
                "emitter_chain": parsed_vaa.emitter_chain,
                "emitter_address": parsed_vaa.emitter_address,
                "sequence": parsed_vaa.sequence,
            }.items()
        )

        if not self.recent_vaas.get(vaa_unique_set):
            needs_db_store = True
            try:
                uinque_set_record_added = await self.unique_set.publish(
                    message=UniqueSetMessage(
                        dest_chain_id=parsed_vaa.payload.dest_chain_id,
                        to_address=parsed_vaa.payload.to_address,
                        from_address=parsed_vaa.payload.from_address,
                        sequence=parsed_vaa.sequence,
                        emitter_chain=parsed_vaa.emitter_chain,
                        emitter_address=parsed_vaa.emitter_address,
                        vaa_hex=vaa_hex,
                    )
                )
            except UniqueSetException as e:
                error = e.detail
                status = Status.FAILED
                cache_status = CacheStatus.CURRENTLY_CACHED
            else:
                if uinque_set_record_added:
                    error = None
                    status = Status.PENDING
                    cache_status = CacheStatus.NEVER_CACHED
                else:
                    needs_db_store = False

            if needs_db_store:
                # Store in database
                await self.transactions_repo.create(
                    transaction=CreateRepoAdapter(
                        emitter_address=parsed_vaa.emitter_address,
                        from_address=parsed_vaa.payload.from_address,
                        to_address=f"0x{parsed_vaa.payload.to_address:040x}",
                        source_chain_id=parsed_vaa.emitter_chain,
                        dest_chain_id=parsed_vaa.payload.dest_chain_id,
                        amount=parsed_vaa.payload.amount,
                        sequence=parsed_vaa.sequence,
                        relay_error=error,
                        relay_status=status,
                        relay_message=vaa_hex,
                        relay_cache_status=cache_status,
                    ),
                )

            if len(self.recent_vaas) >= 100:
                # Remove the oldest (from beginning)
                self.recent_vaas.pop(next(iter(self.recent_vaas)))

            # Add the newest (to end)
            self.recent_vaas[vaa_unique_set] = True

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
        from_address_bytes, dest_chain_id, to_address_uint256, amount = decode_abi(
            types, payload
        )

        return ParsedPayload(
            from_address="0x" + str(from_address_bytes.hex()),
            to_address=to_address_uint256,
            dest_chain_id=dest_chain_id,
            amount=amount,
        )
