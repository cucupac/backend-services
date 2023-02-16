import click
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import (
    get_client_session,
    get_connection,
    get_event_loop,
    get_stream_client,
)
from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.web.endpoints.metrics import health
from app.settings import settings


def setup_app() -> FastAPI:
    app = FastAPI(
        title="Ax Protocol Spy Listener",
        description="Facilitates message passing between chains.",
        openapi_url=settings.openapi_url,
    )
    app.include_router(health.health_router, prefix="/metrics/health")

    # CORS (Cross-Origin Resource Sharing)
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


fastapi_app = setup_app()


@fastapi_app.on_event("startup")
async def startup_event() -> None:
    await get_event_loop()
    await get_client_session()
    await get_or_create_database()
    stream_client = await get_stream_client()
    await stream_client.start()


@fastapi_app.on_event("shutdown")
async def shutdown_event() -> None:
    # Close RabbitMQ connection
    connection = await get_connection()
    await connection.close()
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
        port=settings.spy_listener_server_port,
        **kwargs,
    )
