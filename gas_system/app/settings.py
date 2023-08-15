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
    db_schema: str

    # EVM
    fee_setter_private_key: str
    fee_setter_address: str
    relayer_address: str
    evm_wormhole_bridge: str
    priority_fee_percentile: int
    recent_blocks: int = 100

    # Fee Updates
    higher_ethereum_fee_multiplier: float
    lower_ethereum_fee_multiplier: float
    remote_fee_multiplier: float
    max_acceptable_fee_multiplier: int = 2
    ethereum_update_frequency: int = 60 * 60 * 24
    binance_update_frequency: int = 60 * 60
    polygon_update_frequency: int = 60 * 60
    avalanche_update_frequency: int = 60 * 60
    fantom_update_frequency: int = 60 * 30
    arbitrum_update_frequency: int = 60 * 60
    celo_update_frequency: int = 60 * 30
    optimism_update_frequency: int = 60 * 60

    # RPC Urls
    ethereum_rpc: str
    bsc_rpc: str
    polygon_rpc: str
    avalanche_rpc: str
    fantom_rpc: str
    arbitrum_rpc: str
    celo_rpc: str
    optimism_rpc: str

    # Price Client
    price_client_base_url: str

    # Tasks TODO: change back to once a day
    update_fees_task_frequency: int = 60

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
