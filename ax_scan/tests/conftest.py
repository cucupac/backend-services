# pylint: disable=redefined-outer-name, unused-argument, too-many-arguments
import os
import random
from datetime import datetime, timedelta
from typing import List, Mapping

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

import tests.constants as constant
from app.dependencies import CHAIN_DATA, get_transactions_repo, logger
from app.infrastructure.db.repos.block_record import BlockRecordRepo
from app.infrastructure.db.repos.messages import MessagesRepo
from app.infrastructure.db.repos.mints import MintsRepo
from app.infrastructure.db.repos.points import PointsRepo
from app.infrastructure.db.repos.tasks import TasksRepo
from app.infrastructure.db.repos.transactions import TransactionsRepo
from app.infrastructure.web.setup import setup_app
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.repos.block_record import IBlockRecordRepo
from app.usecases.interfaces.repos.messages import IMessagesRepo
from app.usecases.interfaces.repos.mints import IMintsRepo
from app.usecases.interfaces.repos.points import IPointsRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.tasks.gather_transfer_events import (
    IGatherTransferEventsTask,
)
from app.usecases.schemas.bridge import Bridges
from app.usecases.schemas.cross_chain_message import LzMessage, WhMessage
from app.usecases.schemas.cross_chain_transaction import (
    CrossChainTransaction,
    UpdateCrossChainTransaction,
)
from app.usecases.schemas.evm_transaction import (
    EvmTransaction,
    EvmTransactionStatus,
    UpdateEvmTransaction,
)
from app.usecases.schemas.tasks import TaskInDb, TaskName
from app.usecases.tasks.gather_transfer_events import GatherTransferEventsTask
from app.usecases.tasks.verify_transactions import VerifyTransactionsTask

# Mocks
from tests.mocks.clients.evm import (
    EvmResult,
    MockEvmClientBlockRange,
    MockEvmClientDestOnly,
    MockEvmClientInsertFlow,
    MockEvmClientSrcOnly,
    MockEvmClientTxReciept,
)


# Database Connection
@pytest_asyncio.fixture
async def test_db_url():
    username = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5444")
    database_name = os.getenv("POSTGRES_DB", "ax_services_dev_test")
    return f"postgres://{username}:{password}@{host}:{port}/{database_name}"


@pytest_asyncio.fixture
async def test_db(test_db_url) -> Database:
    test_db = Database(url=test_db_url, min_size=5)

    await test_db.connect()
    yield test_db
    await test_db.execute("TRUNCATE ax_scan.wormhole_messages CASCADE")
    await test_db.execute("TRUNCATE ax_scan.layer_zero_messages CASCADE")
    await test_db.execute("TRUNCATE ax_scan.cross_chain_transactions CASCADE")
    await test_db.execute("TRUNCATE ax_scan.evm_transactions CASCADE")
    await test_db.execute("TRUNCATE ax_scan.block_record CASCADE")
    await test_db.execute("TRUNCATE ax_scan.mints CASCADE")
    await test_db.execute("TRUNCATE ax_scan.points CASCADE")
    await test_db.execute("TRUNCATE ax_scan.task_locks CASCADE")
    await test_db.execute("TRUNCATE ax_scan.tasks CASCADE")
    await test_db.disconnect()


# Repos (Database Gateways)
@pytest_asyncio.fixture
async def messages_repo(test_db: Database) -> IMessagesRepo:
    return MessagesRepo(db=test_db)


@pytest_asyncio.fixture
async def transactions_repo(test_db: Database) -> ITransactionsRepo:
    return TransactionsRepo(db=test_db)


@pytest_asyncio.fixture
async def tasks_repo(test_db: Database, inserted_tasks: None) -> ITasksRepo:
    return TasksRepo(db=test_db)


@pytest_asyncio.fixture
async def block_record_repo(test_db: Database) -> IBlockRecordRepo:
    return BlockRecordRepo(db=test_db)


@pytest_asyncio.fixture
async def mints_repo(test_db: Database) -> IMintsRepo:
    return MintsRepo(db=test_db)


@pytest_asyncio.fixture
async def points_repo(test_db: Database) -> IPointsRepo:
    return PointsRepo(db=test_db)


# Clients
@pytest_asyncio.fixture
async def evm_clients_success_insert() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientInsertFlow(
            result=EvmResult.SUCCESS, chain_id=ax_chain_id
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def evm_clients_dest_only() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientDestOnly(
            result=EvmResult.SUCCESS,
            chain_id=ax_chain_id,
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def evm_clients_src_only() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientSrcOnly(
            result=EvmResult.SUCCESS,
            chain_id=ax_chain_id,
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def evm_clients_block_range_gt() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientBlockRange(
            result=EvmResult.SUCCESS,
            greater_than_max_range=True,
            chain_id=ax_chain_id,
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def evm_clients_block_range_lt() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientBlockRange(
            result=EvmResult.SUCCESS,
            greater_than_max_range=False,
            chain_id=ax_chain_id,
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def evm_clients_tx_receipt_found_status_is_one() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientTxReciept(
            result=EvmResult.SUCCESS,
            tx_exists=True,
            status_is_one=True,
            chain_id=ax_chain_id,
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def evm_clients_tx_receipt_found_status_not_one() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientTxReciept(
            result=EvmResult.SUCCESS,
            tx_exists=True,
            status_is_one=False,
            chain_id=ax_chain_id,
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def evm_clients_tx_receipt_not_found() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientTxReciept(
            result=EvmResult.FAILURE,
            tx_exists=False,
            status_is_one=False,
            chain_id=ax_chain_id,
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def evm_clients_tx_receipt_general_error() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientTxReciept(
            result=EvmResult.FAILURE,
            tx_exists=True,
            status_is_one=False,
            chain_id=ax_chain_id,
        )
    return supported_evm_clients


# Tasks
@pytest_asyncio.fixture
async def gather_events_task_insert(
    test_db: Database,
    evm_clients_success_insert: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    messages_repo: IMessagesRepo,
    block_record_repo: IBlockRecordRepo,
    tasks_repo: ITasksRepo,
) -> IGatherTransferEventsTask:
    return GatherTransferEventsTask(
        db=test_db,
        supported_evm_clients=evm_clients_success_insert,
        transactions_repo=transactions_repo,
        messages_repo=messages_repo,
        block_record_repo=block_record_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def gather_events_task_src_data_first_update(
    test_db: Database,
    evm_clients_dest_only: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    messages_repo: IMessagesRepo,
    block_record_repo: IBlockRecordRepo,
    tasks_repo: ITasksRepo,
) -> IGatherTransferEventsTask:
    return GatherTransferEventsTask(
        db=test_db,
        supported_evm_clients=evm_clients_dest_only,
        transactions_repo=transactions_repo,
        messages_repo=messages_repo,
        block_record_repo=block_record_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def gather_events_task_dest_data_first_update(
    test_db: Database,
    evm_clients_src_only: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    messages_repo: IMessagesRepo,
    block_record_repo: IBlockRecordRepo,
    tasks_repo: ITasksRepo,
) -> IGatherTransferEventsTask:
    return GatherTransferEventsTask(
        db=test_db,
        supported_evm_clients=evm_clients_src_only,
        transactions_repo=transactions_repo,
        messages_repo=messages_repo,
        block_record_repo=block_record_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def gather_events_task_block_range_gt(
    test_db: Database,
    evm_clients_block_range_gt: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    messages_repo: IMessagesRepo,
    block_record_repo: IBlockRecordRepo,
    tasks_repo: ITasksRepo,
) -> IGatherTransferEventsTask:
    return GatherTransferEventsTask(
        db=test_db,
        supported_evm_clients=evm_clients_block_range_gt,
        transactions_repo=transactions_repo,
        messages_repo=messages_repo,
        block_record_repo=block_record_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def gather_events_task_block_range_lt(
    test_db: Database,
    evm_clients_block_range_lt: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    messages_repo: IMessagesRepo,
    block_record_repo: IBlockRecordRepo,
    tasks_repo: ITasksRepo,
) -> IGatherTransferEventsTask:
    return GatherTransferEventsTask(
        db=test_db,
        supported_evm_clients=evm_clients_block_range_lt,
        transactions_repo=transactions_repo,
        messages_repo=messages_repo,
        block_record_repo=block_record_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def verify_transactions_task_found_status_is_one(
    evm_clients_tx_receipt_found_status_is_one: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    tasks_repo: ITasksRepo,
) -> IGatherTransferEventsTask:
    return VerifyTransactionsTask(
        supported_evm_clients=evm_clients_tx_receipt_found_status_is_one,
        transactions_repo=transactions_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def verify_transactions_task_found_status_not_one(
    evm_clients_tx_receipt_found_status_not_one: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    tasks_repo: ITasksRepo,
) -> IGatherTransferEventsTask:
    return VerifyTransactionsTask(
        supported_evm_clients=evm_clients_tx_receipt_found_status_not_one,
        transactions_repo=transactions_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def verify_transactions_task_not_found(
    evm_clients_tx_receipt_not_found: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    tasks_repo: ITasksRepo,
) -> IGatherTransferEventsTask:
    return VerifyTransactionsTask(
        supported_evm_clients=evm_clients_tx_receipt_not_found,
        transactions_repo=transactions_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def verify_transactions_task_general_error(
    evm_clients_tx_receipt_general_error: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    tasks_repo: ITasksRepo,
) -> IGatherTransferEventsTask:
    return VerifyTransactionsTask(
        supported_evm_clients=evm_clients_tx_receipt_general_error,
        transactions_repo=transactions_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


# Enitites
@pytest_asyncio.fixture
async def test_wormhole_message() -> WhMessage:
    return WhMessage(
        emitter_address=constant.WH_EMITTER_ADDRESS,
        source_chain_id=constant.WH_SRC_CHAIN_ID,
        sequence=constant.TEST_MESSAGE_ID,
    )


@pytest_asyncio.fixture
async def test_layer_zero_message() -> LzMessage:
    return LzMessage(
        emitter_address=constant.LZ_EMITTER_ADDRESS,
        source_chain_id=constant.LZ_SRC_CHAIN_ID,
        dest_chain_id=constant.LZ_DEST_CHAIN_ID,
        nonce=constant.TEST_MESSAGE_ID,
    )


@pytest_asyncio.fixture
async def test_wh_evm_tx_src() -> EvmTransaction:
    return EvmTransaction(
        chain_id=constant.TEST_SRC_CHAIN_ID,
        transaction_hash=constant.WH_SRC_TX_HASH,
        block_hash=constant.WH_SRC_BLOCK_HASH,
        block_number=constant.WH_SRC_BLOCK_NUMBER,
        status=EvmTransactionStatus.PENDING,
        gas_price=None,
        gas_used=None,
        error=None,
    )


@pytest_asyncio.fixture
async def test_wh_evm_tx_dest() -> EvmTransaction:
    return EvmTransaction(
        chain_id=constant.TEST_DEST_CHAIN_ID,
        transaction_hash=constant.WH_DEST_TX_HASH,
        block_hash=constant.WH_DEST_BLOCK_HASH,
        block_number=constant.WH_DEST_BLOCK_NUMBER,
        status=EvmTransactionStatus.PENDING,
        gas_price=None,
        gas_used=None,
        error=None,
    )


@pytest_asyncio.fixture
async def test_lz_evm_tx_src() -> EvmTransaction:
    return EvmTransaction(
        chain_id=constant.TEST_SRC_CHAIN_ID,
        transaction_hash=constant.LZ_SRC_TX_HASH,
        block_hash=constant.LZ_SRC_BLOCK_HASH,
        block_number=constant.LZ_SRC_BLOCK_NUMBER,
        status=EvmTransactionStatus.PENDING,
        gas_price=None,
        gas_used=None,
        error=None,
    )


@pytest_asyncio.fixture
async def test_lz_evm_tx_dest() -> EvmTransaction:
    return EvmTransaction(
        chain_id=constant.TEST_DEST_CHAIN_ID,
        transaction_hash=constant.LZ_DEST_TX_HASH,
        block_hash=constant.LZ_DEST_BLOCK_HASH,
        block_number=constant.LZ_DEST_BLOCK_NUMBER,
        status=EvmTransactionStatus.PENDING,
        gas_price=None,
        gas_used=None,
        error=None,
    )


@pytest_asyncio.fixture
async def test_mint_evm_tx() -> EvmTransaction:
    return EvmTransaction(
        chain_id=constant.TEST_MINT_CHAIN_ID,
        transaction_hash=constant.TEST_MINT_TX_HASH,
        block_hash=constant.TEST_MINT_BLOCK_HASH,
        block_number=constant.TEST_MINT_BLOCK_NUMBER,
        status=EvmTransactionStatus.PENDING,
        gas_price=None,
        gas_used=None,
        error=None,
    )


@pytest_asyncio.fixture
async def test_wh_cross_chain_tx_src_data(
    inserted_wh_evm_tx_src: int,
) -> CrossChainTransaction:
    """Notes:
    [1] source-chain tx id comes from evm tx insertion
    [2] mimics data populations form a SendToChain event
    """

    return CrossChainTransaction(
        bridge=Bridges.WORMHOLE,
        from_address=constant.TEST_FROM_ADDRESS,
        to_address=None,
        source_chain_id=constant.TEST_SRC_CHAIN_ID,
        dest_chain_id=constant.TEST_DEST_CHAIN_ID,
        amount=constant.TEST_AMOUNT,
        source_chain_tx_id=inserted_wh_evm_tx_src,
        dest_chain_tx_id=None,
    )


@pytest_asyncio.fixture
async def test_wh_cross_chain_tx_dest_data(
    inserted_wh_evm_tx_dest: int,
) -> CrossChainTransaction:
    """Notes:
    [1] source-chain tx id comes from evm tx insertion
    [2] mimics data populations form a ReceiveFromChian event
    """

    return CrossChainTransaction(
        bridge=Bridges.WORMHOLE,
        from_address=None,
        to_address=constant.TEST_TO_ADDRESS,
        source_chain_id=constant.TEST_SRC_CHAIN_ID,
        dest_chain_id=constant.TEST_DEST_CHAIN_ID,
        amount=constant.TEST_AMOUNT,
        source_chain_tx_id=None,
        dest_chain_tx_id=inserted_wh_evm_tx_dest,
    )


@pytest_asyncio.fixture
async def test_lz_cross_chain_tx_src_data(
    inserted_lz_evm_tx_src: int,
) -> CrossChainTransaction:
    """Notes:
    [1] source-chain tx id comes from evm tx insertion
    [2] mimics data populations form a SendToChain event
    """

    return CrossChainTransaction(
        bridge=Bridges.LAYER_ZERO,
        from_address=constant.TEST_FROM_ADDRESS,
        to_address=None,
        source_chain_id=constant.TEST_SRC_CHAIN_ID,
        dest_chain_id=constant.TEST_DEST_CHAIN_ID,
        amount=constant.TEST_AMOUNT,
        source_chain_tx_id=inserted_lz_evm_tx_src,
        dest_chain_tx_id=None,
    )


@pytest_asyncio.fixture
async def test_lz_cross_chain_tx_dest_data(
    inserted_lz_evm_tx_dest: int,
) -> CrossChainTransaction:
    """Notes:
    [1] source-chain tx id comes from evm tx insertion
    [2] mimics data populations form a ReceiveFromChain event
    """

    return CrossChainTransaction(
        bridge=Bridges.LAYER_ZERO,
        from_address=None,
        to_address=constant.TEST_TO_ADDRESS,
        source_chain_id=constant.TEST_SRC_CHAIN_ID,
        dest_chain_id=constant.TEST_DEST_CHAIN_ID,
        amount=constant.TEST_AMOUNT,
        source_chain_tx_id=None,
        dest_chain_tx_id=inserted_lz_evm_tx_dest,
    )


# Database-inserted Objects
@pytest_asyncio.fixture
async def inserted_wh_evm_tx_src(
    transactions_repo: ITransactionsRepo, test_wh_evm_tx_src: EvmTransaction
) -> int:
    """[WH flow - #1]: Inserts src evm tx."""
    return await transactions_repo.create_evm_tx(evm_tx=test_wh_evm_tx_src)


@pytest_asyncio.fixture
async def inserted_wh_evm_tx_dest(
    transactions_repo: ITransactionsRepo, test_wh_evm_tx_dest: EvmTransaction
) -> int:
    """[WH flow - #1]: Inserts dest evm tx."""
    return await transactions_repo.create_evm_tx(evm_tx=test_wh_evm_tx_dest)


@pytest_asyncio.fixture
async def inserted_lz_evm_tx_src(
    transactions_repo: ITransactionsRepo, test_lz_evm_tx_src: EvmTransaction
) -> int:
    """[LZ flow - #1]: Inserts src evm tx."""
    return await transactions_repo.create_evm_tx(evm_tx=test_lz_evm_tx_src)


@pytest_asyncio.fixture
async def inserted_lz_evm_tx_dest(
    transactions_repo: ITransactionsRepo, test_lz_evm_tx_dest: EvmTransaction
) -> int:
    """[LZ flow - #1]: Inserts src evm tx."""
    return await transactions_repo.create_evm_tx(evm_tx=test_lz_evm_tx_dest)


@pytest_asyncio.fixture
async def inserted_mint_tx(
    transactions_repo: ITransactionsRepo, test_mint_evm_tx: EvmTransaction
) -> int:
    """[LZ flow - #1]: Inserts src evm tx."""
    return await transactions_repo.create_evm_tx(evm_tx=test_mint_evm_tx)


@pytest_asyncio.fixture
async def mixed_status_evm_txs(
    transactions_repo: ITransactionsRepo, test_wh_evm_tx_src: EvmTransaction
) -> None:
    """Evm transactions with mixed statuses."""
    for i in range(4):
        if i % 2 == 0:
            test_wh_evm_tx_src.status = EvmTransactionStatus.PENDING
        elif i == 1:
            test_wh_evm_tx_src.status = EvmTransactionStatus.SUCCESS
        elif i == 3:
            test_wh_evm_tx_src.status = EvmTransactionStatus.SUCCESS

        test_wh_evm_tx_src.transaction_hash += str(i)

        await transactions_repo.create_evm_tx(evm_tx=test_wh_evm_tx_src)


@pytest_asyncio.fixture
async def inserted_wh_cross_chain_tx_src_data(
    transactions_repo: ITransactionsRepo,
    test_wh_cross_chain_tx_src_data: CrossChainTransaction,
) -> int:
    """[WH flow - #2]: Inserts src evm tx and cross-chain tx with src data."""
    return await transactions_repo.create_cross_chain_tx(
        cross_chain_tx=test_wh_cross_chain_tx_src_data
    )


@pytest_asyncio.fixture
async def inserted_wh_cross_chain_tx_dest_data(
    transactions_repo: ITransactionsRepo,
    test_wh_cross_chain_tx_dest_data: CrossChainTransaction,
) -> int:
    """[WH flow - #2]: Inserts dest evm tx and cross-chain tx with dest data."""
    return await transactions_repo.create_cross_chain_tx(
        cross_chain_tx=test_wh_cross_chain_tx_dest_data
    )


@pytest_asyncio.fixture
async def inserted_lz_cross_chain_tx_src_data(
    transactions_repo: ITransactionsRepo,
    test_lz_cross_chain_tx_src_data: CrossChainTransaction,
) -> int:
    """[LZ flow - #2]: Inserts src evm tx and cross-chain tx with src data."""
    return await transactions_repo.create_cross_chain_tx(
        cross_chain_tx=test_lz_cross_chain_tx_src_data
    )


@pytest_asyncio.fixture
async def inserted_lz_cross_chain_tx_dest_data(
    transactions_repo: ITransactionsRepo,
    test_lz_cross_chain_tx_dest_data: CrossChainTransaction,
) -> int:
    """[LZ flow - #2]: Inserts dest evm tx and cross-chain tx with dest data."""
    return await transactions_repo.create_cross_chain_tx(
        cross_chain_tx=test_lz_cross_chain_tx_dest_data
    )


@pytest_asyncio.fixture
async def inserted_wh_message_src_data(
    messages_repo: IMessagesRepo,
    inserted_wh_cross_chain_tx_src_data: int,
    test_wormhole_message: WhMessage,
) -> None:
    """[WH flow - #3]: Inserts src evm tx, cross-chain tx with src data, and corresponding wh message."""
    await messages_repo.create_wormhole_message(
        cross_chain_tx_id=inserted_wh_cross_chain_tx_src_data,
        message=test_wormhole_message,
    )


@pytest_asyncio.fixture
async def inserted_wh_message_dest_data(
    messages_repo: IMessagesRepo,
    inserted_wh_cross_chain_tx_dest_data: int,
    test_wormhole_message: WhMessage,
) -> None:
    """[WH flow - #3]: Inserts dest evm tx, cross_chain_tx with dest data, and corresponding wh message."""
    await messages_repo.create_wormhole_message(
        cross_chain_tx_id=inserted_wh_cross_chain_tx_dest_data,
        message=test_wormhole_message,
    )


@pytest_asyncio.fixture
async def inserted_lz_message_src_data(
    messages_repo: IMessagesRepo,
    inserted_lz_cross_chain_tx_src_data: int,
    test_layer_zero_message: LzMessage,
) -> None:
    """[LZ flow - #3]: Inserts src evm tx, cross-chain tx with src data, and corresponding lz message."""
    await messages_repo.create_layer_zero_message(
        cross_chain_tx_id=inserted_lz_cross_chain_tx_src_data,
        message=test_layer_zero_message,
    )


@pytest_asyncio.fixture
async def inserted_lz_message_dest_data(
    messages_repo: IMessagesRepo,
    inserted_lz_cross_chain_tx_dest_data: int,
    test_layer_zero_message: LzMessage,
) -> None:
    """[LZ flow - #3]: Inserts dest evm tx, cross-chain tx with dest data, and corresponding lz message."""
    await messages_repo.create_layer_zero_message(
        cross_chain_tx_id=inserted_lz_cross_chain_tx_dest_data,
        message=test_layer_zero_message,
    )


@pytest_asyncio.fixture
async def complete_successful_cross_chain_tx(
    messages_repo: IMessagesRepo,
    transactions_repo: ITransactionsRepo,
    inserted_wh_cross_chain_tx_src_data: int,
    inserted_wh_evm_tx_dest: int,
    test_wormhole_message: WhMessage,
    test_db: Database,
) -> None:
    """Setup fixtures include a destination EVM transactions to complete the picture."""
    # 1. Insert a wormhole message (one-to-one with cross_chain_tx)
    await messages_repo.create_wormhole_message(
        cross_chain_tx_id=inserted_wh_cross_chain_tx_src_data,
        message=test_wormhole_message,
    )

    # 2. Update the cross-chain transaction
    await transactions_repo.update_cross_chain_tx(
        cross_chain_tx_id=inserted_wh_cross_chain_tx_src_data,
        update_values=UpdateCrossChainTransaction(
            to_address=constant.TEST_TO_ADDRESS,
            dest_chain_tx_id=inserted_wh_evm_tx_dest,
        ),
    )

    # 3. Update evm transaction statuses
    retrieved_cross_chain_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.cross_chain_transactions AS c_c_t WHERE c_c_t.id=:id""",
        {
            "id": inserted_wh_cross_chain_tx_src_data,
        },
    )
    await transactions_repo.update_evm_tx(
        evm_tx_id=retrieved_cross_chain_tx["source_chain_tx_id"],
        update_values=UpdateEvmTransaction(status=EvmTransactionStatus.SUCCESS),
    )
    await transactions_repo.update_evm_tx(
        evm_tx_id=inserted_wh_evm_tx_dest,
        update_values=UpdateEvmTransaction(status=EvmTransactionStatus.SUCCESS),
    )


@pytest_asyncio.fixture
async def failed_cross_chain_tx(
    messages_repo: IMessagesRepo,
    transactions_repo: ITransactionsRepo,
    inserted_wh_cross_chain_tx_src_data: int,
    test_wormhole_message: WhMessage,
    test_db: Database,
) -> None:
    # 1. Insert a wormhole message (one-to-one with cross_chain_tx)
    await messages_repo.create_wormhole_message(
        cross_chain_tx_id=inserted_wh_cross_chain_tx_src_data,
        message=test_wormhole_message,
    )

    # 2. Update evm transaction status to failed
    retrieved_cross_chain_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.cross_chain_transactions AS c_c_t WHERE c_c_t.id=:id""",
        {
            "id": inserted_wh_cross_chain_tx_src_data,
        },
    )
    await transactions_repo.update_evm_tx(
        evm_tx_id=retrieved_cross_chain_tx["source_chain_tx_id"],
        update_values=UpdateEvmTransaction(status=EvmTransactionStatus.FAILED),
    )


@pytest_asyncio.fixture
async def inserted_block_records(test_db: Database) -> None:
    await test_db.execute(
        "INSERT INTO ax_scan.tasks (name) VALUES ('gather_mint_events');"
    )
    task = await test_db.fetch_one(
        """SELECT * FROM ax_scan.tasks AS t WHERE t.name = 'gather_mint_events'"""
    )
    for index, ax_chain_id in enumerate(CHAIN_DATA):
        query = """INSERT INTO ax_scan.block_record (task_id, chain_id, last_scanned_block_number) VALUES (:task_id, :chain_id, :block_number) RETURNING id"""
        values = {"task_id": task["id"], "chain_id": ax_chain_id, "block_number": index}
        await test_db.execute(query, values)


@pytest_asyncio.fixture
async def inserted_block_record(test_db: Database) -> None:
    await test_db.execute("INSERT INTO ax_scan.tasks (name) VALUES ('test_task');")
    task = await test_db.fetch_one(
        """SELECT * FROM ax_scan.tasks AS t WHERE t.name = 'test_task'"""
    )

    query = """INSERT INTO ax_scan.block_record (task_id, chain_id, last_scanned_block_number) VALUES (:task_id, :chain_id, :block_number) RETURNING id"""
    values = {
        "task_id": task["id"],
        "chain_id": constant.TEST_SRC_CHAIN_ID,
        "block_number": constant.TEST_BLOCK_NUMBER,
    }
    await test_db.execute(query, values)


@pytest_asyncio.fixture
async def inserted_tasks(test_db: Database) -> None:
    for name in TaskName:
        query = """INSERT INTO ax_scan.tasks (name) VALUES (:name) RETURNING id"""
        values = {"name": name.value}
        await test_db.execute(query, values)


@pytest_asyncio.fixture
async def stale_locks(test_db: Database, tasks_repo: ITasksRepo, inserted_tasks: None):
    tasks: List[TaskInDb] = await tasks_repo.retrieve_all()

    for task in tasks:
        async with test_db.transaction():
            # Insert an associated lock with a stale timestamp
            stale_timestamp = datetime.utcnow() - timedelta(
                minutes=random.randint(6, 10)
            )
            query = """INSERT INTO ax_scan.task_locks (task_id, created_at) VALUES (:task_id, :created_at)"""
            values = {"task_id": task.id, "created_at": stale_timestamp}
            await test_db.execute(query, values)


# App
@pytest_asyncio.fixture
def test_app(transactions_repo: ITransactionsRepo) -> FastAPI:
    app = setup_app()
    app.dependency_overrides[get_transactions_repo] = lambda: transactions_repo
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
