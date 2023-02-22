from os import path

from pydantic import BaseSettings

# File path to the global .env file
DOTENV_FILE = ".env" if path.isfile(".env") else None


class Settings(BaseSettings):
    """Application Settings and Environment Variables"""

    # Application Settings
    application_name: str = "relayer"
    environment: str = "development"
    log_level: str = "info"
    server_host: str = "0.0.0.0"
    server_port: int = 9000
    server_prefix: str = ""
    openapi_url: str = "/openapi.json"

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

    # RPC Urls
    ethereum_rpc: str
    bsc_rpc: str
    polygon_rpc: str
    avalanche_rpc: str
    fantom_rpc: str
    moonbeam_rpc: str
    arbitrum_rpc: str
    celo_rpc: str

    # EVM
    relayer_private_key: str
    relayer_address: str

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
