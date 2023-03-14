from os import path

from pydantic import BaseSettings

# File path to the global .env file
DOTENV_FILE = ".env" if path.isfile(".env") else None


class Settings(BaseSettings):
    """Application Settings and Environment Variables"""

    # Application Settings
    application_name: str = "spy_listener"
    environment: str = "development"
    log_level: str = "info"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_prefix: str = ""
    openapi_url: str = "/openapi.json"

    # Wormhole
    guardian_spy_url: str
    spy_service_filters: str

    # Database Settings
    db_url: str

    # RabbitMQ
    rmq_host: str
    rmq_port: int
    rmq_username: str
    rmq_password: str
    exchange_name: str
    routing_key: str
    queue_name: str

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
