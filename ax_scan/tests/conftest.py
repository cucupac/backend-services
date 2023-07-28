# pylint: disable=redefined-outer-name
import os

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

import tests.constants as constant
from app.dependencies import get_example_repo
from app.infrastructure.db.repos.transactions import ExampleRepo
from app.usecases.interfaces.repos.transactions import IExample
from app.infrastructure.web.setup import setup_app
from app.usecases.interfaces.services.example import IExample
from app.usecases.services.example import ExampleService

# Mocks


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
    await test_db.execute("TRUNCATE transactions CASCADE")
    await test_db.execute("TRUNCATE relays CASCADE")
    await test_db.disconnect()


# Repos (Database Gateways)
@pytest_asyncio.fixture
async def example_repo(test_db: Database) -> IExample:
    return ExampleRepo(db=test_db)


# Clients


# Services
@pytest_asyncio.fixture
async def example_service() -> IExample:
    return ExampleService


# Database-inserted Objects


# App
@pytest_asyncio.fixture
def test_app(
    example_repo: IExample,
) -> FastAPI:
    app = setup_app()
    app.dependency_overrides[get_example_repo] = lambda: example_repo
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
