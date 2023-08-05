# pylint: disable=redefined-outer-name, unused-argument
import os
import random
from datetime import datetime, timedelta
from typing import List, Mapping

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

from app.dependencies import CHAIN_DATA, logger
import tests.constants as constant
from app.infrastructure.web.setup import setup_app

from app.infrastructure.db.repos.messages import MessagesRepo
from app.infrastructure.db.repos.tasks import TasksRepo
from app.infrastructure.db.repos.transactions import TransactionsRepo

from app.usecases.interfaces.repos.messages import IMessagesRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.tasks.gather_events import IGatherEventsTask
from app.usecases.interfaces.clients.evm import IEvmClient

from app.usecases.schemas.bridge import Bridges
from app.usecases.schemas.cross_chain_message import LzMessage, WhMessage
from app.usecases.schemas.cross_chain_transaction import CrossChainTransaction
from app.usecases.schemas.evm_transaction import EvmTransaction, EvmTransactionStatus
from app.usecases.schemas.tasks import TaskInDb, TaskName

from app.usecases.tasks.gather_events import GatherEventsTask

# Mocks
from tests.mocks.clients.evm import (
    MockEvmClientInsertFlow,
    MockEvmClientUpdateFlow,
    EvmResult,
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


# Clients
@pytest_asyncio.fixture
async def test_evm_clients_success_insert() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientInsertFlow(
            result=EvmResult.SUCCESS, chain_id=ax_chain_id
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def test_evm_clients_update() -> IEvmClient:
    supported_evm_clients = {}
    for ax_chain_id in CHAIN_DATA:
        supported_evm_clients[ax_chain_id] = MockEvmClientUpdateFlow(
            result=EvmResult.SUCCESS,
            chain_id=ax_chain_id,
        )
    return supported_evm_clients


# Services
# @pytest_asyncio.fixture
# async def example_service() -> IExample:
#     return ExampleService


# Tasks
@pytest_asyncio.fixture
async def gather_events_task_insert(
    test_db: Database,
    test_evm_clients_success_insert: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    messages_repo: IMessagesRepo,
    tasks_repo: ITasksRepo,
) -> IGatherEventsTask:
    return GatherEventsTask(
        db=test_db,
        supported_evm_clients=test_evm_clients_success_insert,
        transactions_repo=transactions_repo,
        messages_repo=messages_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def gather_events_task_update(
    test_db: Database,
    test_evm_clients_update: Mapping[int, IEvmClient],
    transactions_repo: ITransactionsRepo,
    messages_repo: IMessagesRepo,
    tasks_repo: ITasksRepo,
) -> IGatherEventsTask:
    return GatherEventsTask(
        db=test_db,
        supported_evm_clients=test_evm_clients_update,
        transactions_repo=transactions_repo,
        messages_repo=messages_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


# Repo Adapters
@pytest_asyncio.fixture
async def test_layer_zero_message() -> LzMessage:
    return LzMessage(
        emitter_address=constant.LZ_EMITTER_ADDRESS,
        source_chain_id=constant.LZ_SOURCE_CHAIN_ID,
        dest_chain_id=constant.LZ_DEST_CHAIN_ID,
        nonce=constant.TEST_MESSAGE_ID,
    )


@pytest_asyncio.fixture
async def test_wormhole_message() -> WhMessage:
    return WhMessage(
        emitter_address=constant.WH_EMITTER_ADDRESS,
        source_chain_id=constant.WH_SOURCE_CHAIN_ID,
        sequence=constant.TEST_MESSAGE_ID,
    )


@pytest_asyncio.fixture
async def test_lz_evm_tx() -> EvmTransaction:
    return EvmTransaction(
        chain_id=constant.TEST_SOURCE_CHAIN_ID,
        transaction_hash=constant.LZ_SOURCE_TX_HASH,
        block_hash=constant.LZ_SOURCE_BLOCK_HASH,
        block_number=constant.LZ_BLOCK_NUMBER,
        status=EvmTransactionStatus.PENDING,
        gas_price=None,
        gas_used=None,
        timestamp=None,
    )


@pytest_asyncio.fixture
async def test_wh_evm_tx() -> EvmTransaction:
    return EvmTransaction(
        chain_id=constant.TEST_SOURCE_CHAIN_ID,
        transaction_hash=constant.WH_SOURCE_TX_HASH,
        block_hash=constant.WH_SOURCE_BLOCK_HASH,
        block_number=constant.WH_SOURCE_BLOCK_NUMBER,
        status=EvmTransactionStatus.PENDING,
        gas_price=None,
        gas_used=None,
        timestamp=None,
    )


@pytest_asyncio.fixture
async def test_wh_dest_evm_tx() -> EvmTransaction:
    return EvmTransaction(
        chain_id=constant.TEST_DEST_CHAIN_ID,
        transaction_hash=constant.WH_DEST_TX_HASH,
        block_hash=constant.WH_DEST_BLOCK_HASH,
        block_number=constant.WH_DEST_BLOCK_NUMBER,
        status=EvmTransactionStatus.PENDING,
        gas_price=None,
        gas_used=None,
        timestamp=None,
    )


@pytest_asyncio.fixture
async def test_lz_cross_chain_tx(
    inserted_lz_evm_transaction: int,
) -> CrossChainTransaction:
    """Note: Source-chain tx id comes from evm tx insertion."""

    return CrossChainTransaction(
        bridge=Bridges.LAYER_ZERO,
        from_address=constant.TEST_FROM_ADDRESS,
        to_address=None,
        source_chain_id=constant.TEST_SOURCE_CHAIN_ID,
        dest_chain_id=constant.TEST_DEST_CHAIN_ID,
        amount=constant.TEST_AMOUNT,
        source_chain_tx_id=inserted_lz_evm_transaction,
        dest_chain_tx_id=None,
    )


@pytest_asyncio.fixture
async def test_wh_cross_chain_tx(
    inserted_wh_evm_transaction: int,
) -> CrossChainTransaction:
    """Note: Source-chain tx id comes from evm tx insertion."""

    return CrossChainTransaction(
        bridge=Bridges.WORMHOLE,
        from_address=constant.TEST_FROM_ADDRESS,
        to_address=None,
        source_chain_id=constant.TEST_SOURCE_CHAIN_ID,
        dest_chain_id=constant.TEST_DEST_CHAIN_ID,
        amount=constant.TEST_AMOUNT,
        source_chain_tx_id=inserted_wh_evm_transaction,
        dest_chain_tx_id=None,
    )


# Database-inserted Objects
@pytest_asyncio.fixture
async def inserted_lz_evm_transaction(
    transactions_repo: ITransactionsRepo, test_lz_evm_tx: EvmTransaction
) -> int:
    """[LZ flow]: Insert #1"""
    return await transactions_repo.create_evm_tx(evm_tx=test_lz_evm_tx)


@pytest_asyncio.fixture
async def inserted_wh_evm_transaction(
    transactions_repo: ITransactionsRepo, test_wh_evm_tx: EvmTransaction
) -> int:
    """[WH flow]: Insert #1"""
    return await transactions_repo.create_evm_tx(evm_tx=test_wh_evm_tx)


@pytest_asyncio.fixture
async def inserted_wh_dest_evm_transaction(
    transactions_repo: ITransactionsRepo, test_wh_dest_evm_tx: EvmTransaction
) -> int:
    return await transactions_repo.create_evm_tx(evm_tx=test_wh_dest_evm_tx)


@pytest_asyncio.fixture
async def inserted_lz_cross_chain_tx(
    transactions_repo: ITransactionsRepo, test_lz_cross_chain_tx: CrossChainTransaction
) -> int:
    """[LZ flow]: Insert #2"""
    return await transactions_repo.create_cross_chain_tx(
        cross_chain_tx=test_lz_cross_chain_tx
    )


@pytest_asyncio.fixture
async def inserted_wh_cross_chain_tx(
    transactions_repo: ITransactionsRepo, test_wh_cross_chain_tx: CrossChainTransaction
) -> int:
    """[WH flow]: Insert #2"""
    return await transactions_repo.create_cross_chain_tx(
        cross_chain_tx=test_wh_cross_chain_tx
    )


@pytest_asyncio.fixture
async def inserted_wormhole_message(
    messages_repo: IMessagesRepo,
    inserted_wh_cross_chain_tx: int,
    test_wormhole_message: WhMessage,
) -> None:
    """[WH flow]: Insert #3"""
    await messages_repo.create_wormhole_message(
        cross_chain_tx_id=inserted_wh_cross_chain_tx,
        message=test_wormhole_message,
    )


@pytest_asyncio.fixture
async def inserted_layer_zero_message(
    messages_repo: IMessagesRepo,
    inserted_lz_cross_chain_tx: int,
    test_layer_zero_message: LzMessage,
) -> None:
    """[LZ flow]: Insert #3"""
    await messages_repo.create_layer_zero_message(
        cross_chain_tx_id=inserted_lz_cross_chain_tx,
        message=test_layer_zero_message,
    )


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
def test_app(
    # example_repo: IExample,
) -> FastAPI:
    app = setup_app()
    # app.dependency_overrides[get_example_repo] = lambda: example_repo
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
