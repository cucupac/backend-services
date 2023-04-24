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
    reconnect_wait_time: int

    # Database Settings
    db_url: str

    # Redis
    redis_consumption_frequency: int = 1
    redis_reconnect_frequency: int = 5
    redis_in_memory_cache_periodicity: int = 15
    redis_min_message_age: int = 10
    redis_zset: str
    redis_url: str

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
