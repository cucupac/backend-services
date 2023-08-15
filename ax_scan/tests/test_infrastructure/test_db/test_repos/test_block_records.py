# pylint: disable=unused-argument
import pytest
from databases import Database


from app.dependencies import CHAIN_DATA
from app.usecases.interfaces.repos.block_record import IBlockRecordRepo
from app.usecases.schemas.block_record import BlockRecordInDb, BlockRecord
from app.usecases.schemas.blockchain import AxChains


@pytest.mark.asyncio
async def test_upsert(block_record_repo: IBlockRecordRepo, test_db: Database) -> None:
    """Tests that a block record is creacted correctly."""

    block_records = await test_db.fetch_all("""SELECT * FROM ax_scan.block_record""")

    assert len(block_records) == 0

    # Create
    initial_data = {}
    for index, ax_chain_id in enumerate(CHAIN_DATA):
        initial_data[ax_chain_id] = index
        await block_record_repo.upsert(
            block_record=BlockRecord(
                chain_id=ax_chain_id, last_scanned_block_number=index
            )
        )

    block_records = await test_db.fetch_all("""SELECT * FROM ax_scan.block_record""")

    assert len(block_records) == len(CHAIN_DATA)

    checked_chain_ids = []
    for block_record in block_records:
        assert block_record["chain_id"] not in checked_chain_ids
        assert AxChains(block_record["chain_id"])
        assert (
            block_record["last_scanned_block_number"]
            == initial_data[block_record["chain_id"]]
        )
        checked_chain_ids.append(checked_chain_ids)

    # Update
    post_update_data = {}
    for index, ax_chain_id in enumerate(CHAIN_DATA):
        block_num = 2 * index
        post_update_data[ax_chain_id] = block_num
        await block_record_repo.upsert(
            block_record=BlockRecord(
                chain_id=ax_chain_id, last_scanned_block_number=block_num
            )
        )

    block_records = await test_db.fetch_all("""SELECT * FROM ax_scan.block_record""")

    checked_chain_ids = []
    assert len(block_records) == len(CHAIN_DATA)
    for block_record in block_records:
        assert block_record["chain_id"] not in checked_chain_ids
        assert AxChains(block_record["chain_id"])
        assert (
            block_record["last_scanned_block_number"]
            == post_update_data[block_record["chain_id"]]
        )
        checked_chain_ids.append(checked_chain_ids)


@pytest.mark.asyncio
async def test_retrieve(
    block_record_repo: IBlockRecordRepo, inserted_block_records: None
) -> None:
    """Tests that a block record can be retrieved by chain ID."""

    # Act
    for ax_chain_id in CHAIN_DATA:
        block_record = await block_record_repo.retrieve(chain_id=ax_chain_id)
        assert isinstance(block_record, BlockRecordInDb)
        assert block_record.chain_id == ax_chain_id
