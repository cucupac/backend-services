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
    server_port: int = 10000
    server_prefix: str = ""
    openapi_url: str = "/openapi.json"

    # Database Settings
    db_url: str

    # EVM
    fee_setter_private_key: str
    fee_setter_address: str
    mock_fee: int
    evm_wormhole_bridge: str
    priority_fee_percentile: int
    remote_fee_multiplier: float

    # RPC Urls
    ethereum_rpc: str
    bsc_rpc: str
    polygon_rpc: str
    avalanche_rpc: str
    fantom_rpc: str
    arbitrum_rpc: str
    celo_rpc: str

    # Price Client
    price_client_base_url: str

    # Tasks TODO: change back to once a day
    update_fees_frequency: int = 30

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
