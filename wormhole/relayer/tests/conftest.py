# pylint: disable=redefined-outer-name,unused-argument
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
from app.dependencies import CHAIN_DATA, get_relays_repo, logger
from app.infrastructure.clients.websocket import WebsocketClient
from app.infrastructure.db.repos.relays import RelaysRepo
from app.infrastructure.db.repos.tasks import TasksRepo
from app.infrastructure.web.setup import setup_app
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.clients.websocket import IWebsocketClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.services.message_processor import IVaaProcessor
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.interfaces.tasks.gather_missed import IGatherMissedVaasTask
from app.usecases.interfaces.tasks.manage_locks import IManageLocksTask
from app.usecases.interfaces.tasks.retry_failed import IRetryFailedTask
from app.usecases.interfaces.tasks.verify_delivery import IVerifyDeliveryTask
from app.usecases.schemas.relays import (
    CacheStatus,
    RelayErrors,
    Status,
    UpdateRepoAdapter,
)
from app.usecases.schemas.tasks import TaskInDb, TaskName
from app.usecases.services.message_processor import MessageProcessor
from app.usecases.services.vaa_delivery import VaaDelivery
from app.usecases.tasks.gather_missed import GatherMissedVaasTask
from app.usecases.tasks.gather_pending import GatherPendingVaasTask
from app.usecases.tasks.manage_locks import ManageLocksTask
from app.usecases.tasks.retry_failed import RetryFailedTask
from app.usecases.tasks.verify_delivery import VerifyDeliveryTask

# Mocks
from tests.mocks.clients.evm import EvmResult, MockEvmClient
from tests.mocks.clients.websocket import MockWebsocketClient
from tests.mocks.clients.wormhole import MockWormholeClient


# Database Connection
@pytest_asyncio.fixture
async def test_db_url() -> str:
    username = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5444")
    database_name = os.getenv("POSTGRES_DB", "ax_relayer_dev_test")
    return f"postgres://{username}:{password}@{host}:{port}/{database_name}"


@pytest_asyncio.fixture
async def test_db(test_db_url) -> Database:
    test_db = Database(url=test_db_url, min_size=5)

    await test_db.connect()
    yield test_db
    await test_db.execute("TRUNCATE transactions CASCADE")
    await test_db.execute("TRUNCATE relays CASCADE")
    await test_db.execute("TRUNCATE tasks CASCADE")
    await test_db.execute("TRUNCATE task_locks CASCADE")
    await test_db.disconnect()


@pytest_asyncio.fixture
async def relays_repo(test_db: Database) -> IRelaysRepo:
    return RelaysRepo(db=test_db)


@pytest_asyncio.fixture
async def tasks_repo(test_db: Database, inserted_tasks: None) -> ITasksRepo:
    return TasksRepo(db=test_db)


@pytest_asyncio.fixture
async def supported_evm_clients_success() -> Mapping[int, IEvmClient]:
    supported_evm_clients = {}
    for chain_id in CHAIN_DATA:
        supported_evm_clients[chain_id] = MockEvmClient(result=EvmResult.SUCCESS)
    return supported_evm_clients


@pytest_asyncio.fixture
async def supported_evm_clients_error() -> Mapping[int, IEvmClient]:
    supported_evm_clients = {}
    for chain_id in CHAIN_DATA:
        supported_evm_clients[chain_id] = MockEvmClient(result=EvmResult.ERROR)
    return supported_evm_clients


@pytest_asyncio.fixture
async def supported_evm_clients_fail() -> Mapping[int, IEvmClient]:
    supported_evm_clients = {}
    for chain_id in CHAIN_DATA:
        supported_evm_clients[chain_id] = MockEvmClient(result=EvmResult.FAILURE)
    return supported_evm_clients


@pytest_asyncio.fixture
async def test_websocket_client() -> IWebsocketClient:
    return MockWebsocketClient()


@pytest_asyncio.fixture
async def websocket_client() -> IWebsocketClient:
    return WebsocketClient(logger=logger)


# Clients
@pytest_asyncio.fixture
async def test_wormhole_client() -> IBridgeClient:
    return MockWormholeClient()


# Services
@pytest_asyncio.fixture
async def vaa_delivery(
    supported_evm_clients_success: IEvmClient,
    relays_repo: IRelaysRepo,
    test_websocket_client: IWebsocketClient,
) -> IVaaDelivery:
    return VaaDelivery(
        relays_repo=relays_repo,
        supported_evm_clients=supported_evm_clients_success,
        websocket_client=test_websocket_client,
        logger=logger,
    )


@pytest_asyncio.fixture
async def vaa_delivery_error(
    supported_evm_clients_error: IEvmClient,
    relays_repo: IRelaysRepo,
    test_websocket_client: IWebsocketClient,
) -> IVaaDelivery:
    return VaaDelivery(
        relays_repo=relays_repo,
        supported_evm_clients=supported_evm_clients_error,
        websocket_client=test_websocket_client,
        logger=logger,
    )


@pytest_asyncio.fixture
async def vaa_delivery_websocket(
    supported_evm_clients_success: IEvmClient,
    relays_repo: IRelaysRepo,
    websocket_client: IWebsocketClient,
) -> IVaaDelivery:
    return VaaDelivery(
        relays_repo=relays_repo,
        supported_evm_clients=supported_evm_clients_success,
        websocket_client=websocket_client,
        logger=logger,
    )


@pytest_asyncio.fixture
async def vaa_delivery_websocket_error(
    supported_evm_clients_error: IEvmClient,
    relays_repo: IRelaysRepo,
    websocket_client: IWebsocketClient,
) -> IVaaDelivery:
    return VaaDelivery(
        relays_repo=relays_repo,
        supported_evm_clients=supported_evm_clients_error,
        websocket_client=websocket_client,
        logger=logger,
    )


@pytest_asyncio.fixture
async def message_processor() -> IVaaProcessor:
    return MessageProcessor()


# Tasks
@pytest_asyncio.fixture
async def verify_delivery_task_success(
    supported_evm_clients_success: Mapping[int, IEvmClient],
    relays_repo: IRelaysRepo,
    tasks_repo: ITasksRepo,
) -> IVerifyDeliveryTask:
    return VerifyDeliveryTask(
        supported_evm_clients=supported_evm_clients_success,
        relays_repo=relays_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def verify_delivery_task_fail(
    supported_evm_clients_fail: Mapping[int, IEvmClient],
    relays_repo: IRelaysRepo,
    tasks_repo: ITasksRepo,
) -> IVerifyDeliveryTask:
    return VerifyDeliveryTask(
        supported_evm_clients=supported_evm_clients_fail,
        relays_repo=relays_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def verify_delivery_task_error(
    supported_evm_clients_error: Mapping[int, IEvmClient],
    relays_repo: IRelaysRepo,
    tasks_repo: ITasksRepo,
) -> IVerifyDeliveryTask:
    return VerifyDeliveryTask(
        supported_evm_clients=supported_evm_clients_error,
        relays_repo=relays_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def retry_failed_task(
    message_processor: IVaaProcessor,
    test_wormhole_client: IBridgeClient,
    supported_evm_clients_success: IEvmClient,
    relays_repo: IRelaysRepo,
    tasks_repo: ITasksRepo,
) -> IRetryFailedTask:
    return RetryFailedTask(
        message_processor=message_processor,
        supported_evm_clients=supported_evm_clients_success,
        bridge_client=test_wormhole_client,
        relays_repo=relays_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def gather_missed_task(
    message_processor: IVaaProcessor,
    test_wormhole_client: IBridgeClient,
    relays_repo: IRelaysRepo,
    tasks_repo: ITasksRepo,
) -> IGatherMissedVaasTask:
    return GatherMissedVaasTask(
        message_processor=message_processor,
        bridge_client=test_wormhole_client,
        relays_repo=relays_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def gather_pending_task(
    relays_repo: IRelaysRepo,
    tasks_repo: ITasksRepo,
) -> IGatherMissedVaasTask:
    return GatherPendingVaasTask(
        relays_repo=relays_repo,
        tasks_repo=tasks_repo,
        logger=logger,
    )


@pytest_asyncio.fixture
async def manage_locks_task(
    tasks_repo: ITasksRepo,
) -> IManageLocksTask:
    return ManageLocksTask(
        tasks_repo=tasks_repo,
        logger=logger,
    )


# Database-inserted Objects
@pytest_asyncio.fixture
async def inserted_transaction(test_db: Database) -> None:
    async with test_db.transaction():
        transaction_id = await test_db.execute(
            """INSERT INTO transactions (emitter_address, from_address, to_address, source_chain_id, dest_chain_id, amount, sequence) VALUES (:emitter_address, :from_address, :to_address, :source_chain_id, :dest_chain_id, :amount, :sequence) RETURNING id""",
            {
                "emitter_address": constant.TEST_EMITTER_ADDRESS,
                "from_address": constant.TEST_USER_ADDRESS,
                "to_address": constant.TEST_USER_ADDRESS,
                "source_chain_id": constant.TEST_SOURCE_CHAIN_ID,
                "dest_chain_id": constant.TEST_DESTINATION_CHAIN_ID,
                "amount": constant.TEST_AMOUNT,
                "sequence": constant.TEST_SEQUENCE,
            },
        )
        await test_db.execute(
            """INSERT INTO relays (transaction_id, message, status, transaction_hash, error, cache_status, grpc_status) VALUES (:transaction_id, :message, :status, :transaction_hash, :error, :cache_status, :grpc_status)""",
            {
                "transaction_id": transaction_id,
                "status": Status.PENDING,
                "error": None,
                "message": constant.TEST_VAA,
                "transaction_hash": None,
                "cache_status": CacheStatus.NEVER_CACHED,
                "grpc_status": "success",
            },
        )


@pytest_asyncio.fixture
async def failed_transaction(test_db: Database) -> None:
    async with test_db.transaction():
        transaction_id = await test_db.execute(
            """INSERT INTO transactions (emitter_address, from_address, to_address, source_chain_id, dest_chain_id, amount, sequence) VALUES (:emitter_address, :from_address, :to_address, :source_chain_id, :dest_chain_id, :amount, :sequence) RETURNING id""",
            {
                "emitter_address": constant.TEST_EMITTER_ADDRESS,
                "from_address": None,
                "to_address": None,
                "source_chain_id": constant.TEST_SOURCE_CHAIN_ID,
                "dest_chain_id": None,
                "amount": None,
                "sequence": constant.TEST_SEQUENCE,
            },
        )
        await test_db.execute(
            """INSERT INTO relays (transaction_id, message, status, transaction_hash, error, cache_status, grpc_status) VALUES (:transaction_id, :message, :status, :transaction_hash, :error, :cache_status, :grpc_status)""",
            {
                "transaction_id": transaction_id,
                "status": Status.FAILED,
                "error": RelayErrors.MISSED_VAA,
                "message": None,
                "transaction_hash": None,
                "cache_status": CacheStatus.NEVER_CACHED,
                "grpc_status": "failed",
            },
        )


@pytest_asyncio.fixture
async def pending_transactions(test_db: Database) -> None:
    for index in range(constant.DEFAULT_ITERATIONS):
        async with test_db.transaction():
            transaction_id = await test_db.execute(
                """INSERT INTO transactions (emitter_address, from_address, to_address, source_chain_id, dest_chain_id, amount, sequence) VALUES (:emitter_address, :from_address, :to_address, :source_chain_id, :dest_chain_id, :amount, :sequence) RETURNING id""",
                {
                    "emitter_address": constant.TEST_EMITTER_ADDRESS,
                    "from_address": constant.TEST_USER_ADDRESS,
                    "to_address": constant.TEST_USER_ADDRESS,
                    "source_chain_id": constant.TEST_SOURCE_CHAIN_ID,
                    "dest_chain_id": constant.TEST_DESTINATION_CHAIN_ID,
                    "amount": constant.TEST_AMOUNT,
                    "sequence": constant.TEST_SEQUENCE + index,
                },
            )
            await test_db.execute(
                """INSERT INTO relays (transaction_id, message, status, transaction_hash, error, cache_status, grpc_status, created_at) VALUES (:transaction_id, :message, :status, :transaction_hash, :error, :cache_status, :grpc_status, :created_at)""",
                {
                    "transaction_id": transaction_id,
                    "status": Status.PENDING,
                    "error": None,
                    "message": constant.TEST_VAA,
                    "transaction_hash": None,
                    "cache_status": CacheStatus.NEVER_CACHED,
                    "grpc_status": "success",
                    "created_at": datetime.utcnow()
                    - timedelta(minutes=random.randint(2, 10)),
                },
            )


@pytest_asyncio.fixture
async def pending_transactions_with_tx_hash(test_db: Database) -> None:
    for index in range(constant.DEFAULT_ITERATIONS):
        async with test_db.transaction():
            transaction_id = await test_db.execute(
                """INSERT INTO transactions (emitter_address, from_address, to_address, source_chain_id, dest_chain_id, amount, sequence) VALUES (:emitter_address, :from_address, :to_address, :source_chain_id, :dest_chain_id, :amount, :sequence) RETURNING id""",
                {
                    "emitter_address": constant.TEST_EMITTER_ADDRESS,
                    "from_address": constant.TEST_USER_ADDRESS,
                    "to_address": constant.TEST_USER_ADDRESS,
                    "source_chain_id": constant.TEST_SOURCE_CHAIN_ID,
                    "dest_chain_id": constant.TEST_DESTINATION_CHAIN_ID,
                    "amount": constant.TEST_AMOUNT,
                    "sequence": constant.TEST_SEQUENCE + index,
                },
            )
            await test_db.execute(
                """INSERT INTO relays (transaction_id, message, status, transaction_hash, error, cache_status, grpc_status) VALUES (:transaction_id, :message, :status, :transaction_hash, :error, :cache_status, :grpc_status)""",
                {
                    "transaction_id": transaction_id,
                    "status": Status.PENDING,
                    "error": None,
                    "message": constant.TEST_VAA,
                    "transaction_hash": constant.TEST_TRANSACTION_HASH,
                    "cache_status": CacheStatus.NEVER_CACHED,
                    "grpc_status": "success",
                },
            )


@pytest_asyncio.fixture
async def inserted_recent_transactions(test_db: Database) -> None:
    for source_chain_id in constant.TEST_MISSED_VAAS_CHAIN_IDS:
        async with test_db.transaction():
            transaction_id = await test_db.execute(
                """INSERT INTO transactions (emitter_address, from_address, to_address, source_chain_id, dest_chain_id, amount, sequence) VALUES (:emitter_address, :from_address, :to_address, :source_chain_id, :dest_chain_id, :amount, :sequence) RETURNING id""",
                {
                    "emitter_address": constant.TEST_EMITTER_ADDRESS,
                    "from_address": None,
                    "to_address": None,
                    "source_chain_id": source_chain_id,
                    "dest_chain_id": None,
                    "amount": None,
                    "sequence": min(constant.TEST_MISSED_VAAS_CELO_SEQUENCES) - 1
                    if source_chain_id == constant.CELO_CHAIN_ID
                    else min(constant.TEST_MISSED_VAAS_POLYGON_SEQUENCES) - 1,
                },
            )
        await test_db.execute(
            """INSERT INTO relays (transaction_id, message, status, transaction_hash, error, cache_status, grpc_status) VALUES (:transaction_id, :message, :status, :transaction_hash, :error, :cache_status, :grpc_status)""",
            {
                "transaction_id": transaction_id,
                "status": Status.FAILED,
                "error": RelayErrors.MISSED_VAA,
                "message": None,
                "transaction_hash": None,
                "cache_status": CacheStatus.NEVER_CACHED,
                "grpc_status": "failed",
            },
        )


@pytest_asyncio.fixture
async def inserted_tasks(test_db: Database) -> None:
    for name in TaskName:
        query = """INSERT INTO tasks (name) VALUES (:name) RETURNING id"""
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
            query = """INSERT INTO task_locks (task_id, created_at) VALUES (:task_id, :created_at)"""
            values = {"task_id": task.id, "created_at": stale_timestamp}
            await test_db.execute(query, values)


# Repo Adapters
@pytest_asyncio.fixture
async def update_relays_repo_adapter() -> UpdateRepoAdapter:
    return UpdateRepoAdapter(
        emitter_address=constant.TEST_EMITTER_ADDRESS,
        source_chain_id=constant.TEST_SOURCE_CHAIN_ID,
        sequence=constant.TEST_SEQUENCE,
        transaction_hash=constant.TEST_TRANSACTION_HASH,
        error=None,
        status=Status.SUCCESS,
    )


@pytest_asyncio.fixture
def test_app(
    relays_repo: IRelaysRepo,
) -> FastAPI:
    app = setup_app()
    app.dependency_overrides[get_relays_repo] = lambda: relays_repo
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
