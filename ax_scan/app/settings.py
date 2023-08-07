from os import path

from pydantic_settings import BaseSettings

# File path to the global .env file
DOTENV_FILE = ".env" if path.isfile(".env") else None


class Settings(BaseSettings):
    """Application Settings and Environment Variables"""

    # Application Settings
    application_name: str = "ax_scan"
    environment: str = "development"
    log_level: str = "info"
    server_host: str = "0.0.0.0"
    server_prefix: str = ""
    openapi_url: str = "/openapi.json"
    server_port: int

    # Database Settings
    db_url: str
    db_schema: str

    # EVM
    send_to_chain_topic: str = (
        "0xf4ba2bafddabe3a9ff1cd1e40eb0beb9a1dba082451a1cb0ff732e40957650b6"
    )
    receive_from_chain_topic: str = (
        "0x64e10c37f404d128982dce114f5d233c14c5c7f6d8db93099e3d99dacb9e27ba"
    )

    # Ax Protocol
    evm_wormhole_bridge: str
    evm_layerzero_bridge: str

    # Tasks
    gather_txs_frequency: int = 60
    verify_txs_frequency: int = 60

    # RPC Urls
    ethereum_rpc: str
    bsc_rpc: str
    polygon_rpc: str
    avalanche_rpc: str
    fantom_rpc: str
    arbitrum_rpc: str
    celo_rpc: str
    optimism_rpc: str
    gnosis_rpc: str

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
