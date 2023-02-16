import click
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import (
    get_client_session,
    get_connection,
    get_event_loop,
    get_rabbitmq_client,
)
from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.web.endpoints.metrics import health
from app.infrastructure.web.endpoints.public import transactions
from app.settings import settings


def setup_app() -> FastAPI:
    fastapi_app = FastAPI(
        title="Ax Protocol Spy Listener",
        description="Facilitates message passing between chains.",
        openapi_url=settings.openapi_url,
    )
    fastapi_app.include_router(health.health_router, prefix="/metrics/health")
    fastapi_app.include_router(
        transactions.transactions_router, prefix="/public/transactions"
    )

    # CORS (Cross-Origin Resource Sharing)
    origins = ["*"]
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return fastapi_app


app = setup_app()


@app.on_event("startup")
async def startup_event() -> None:
    await get_event_loop()
    await get_client_session()
    await get_or_create_database()
    queue_client = await get_rabbitmq_client()
    await queue_client.start_consumption()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    # Close RabbitMQ connection
    queue_connection = await get_connection()
    await queue_connection.close()
    # Close client session
    client_session = await get_client_session()
    await client_session.close()
    # Close database connection
    DATABASE = await get_or_create_database()
    if DATABASE.is_connected:
        await DATABASE.disconnect()


@click.command()
@click.option("--reload", is_flag=True)
def main(reload=False) -> None:
    kwargs = {"reload": reload}
    uvicorn.run(
        "app.infrastructure.web.setup:app",
        loop="uvloop",
        host=settings.server_host,
        port=settings.relayer_server_port,
        **kwargs,
    )
