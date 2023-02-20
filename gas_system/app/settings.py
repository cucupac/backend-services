from os import path

from pydantic import BaseSettings

# File path to the global .env file
DOTENV_FILE = ".env" if path.isfile(".env") else None


class Settings(BaseSettings):
    """Application Settings and Environment Variables"""

    # Application Settings
    application_name: str = "gas_system"
    environment: str = "development"
    log_level: str = "info"
    server_host: str = "0.0.0.0"
    server_port: int
    server_prefix: str = ""
    openapi_url: str = "/openapi.json"

    # Database Settings
    db_url: str

    # EVM
    chain_lookup: str
    admin_private_key: str
    admin_address: str
    wormhole_bridge_abi: str
    mock_fee: int

    # Tasks
    update_fees_frequency: int = 60 * 60 * 24

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
