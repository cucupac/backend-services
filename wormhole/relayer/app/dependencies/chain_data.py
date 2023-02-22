from app.settings import settings

CHAIN_DATA = {
    "1": {
        "rpc": settings.ethereum_rpc,
        "bridge_contract": "0x5a9673073ba5C0F52Aac535EC915D7aE2209A6B6",
        "native": "ETH",
    },
    "56": {
        "rpc": settings.bsc_rpc,
        "bridge_contract": "0x5a9673073ba5C0F52Aac535EC915D7aE2209A6B6",
        "native": "BNB",
    },
    "137": {
        "rpc": settings.polygon_rpc,
        "bridge_contract": "0x5a9673073ba5C0F52Aac535EC915D7aE2209A6B6",
        "native": "MATIC",
    },
    "43114": {
        "rpc": settings.avalanche_rpc,
        "bridge_contract": "0x5a9673073ba5C0F52Aac535EC915D7aE2209A6B6",
        "native": "AVAX",
    },
    "250": {
        "rpc": settings.fantom_rpc,
        "bridge_contract": "0x5a9673073ba5C0F52Aac535EC915D7aE2209A6B6",
        "native": "FTM",
    },
    "1284": {
        "rpc": settings.moonbeam_rpc,
        "bridge_contract": "0x5a9673073ba5C0F52Aac535EC915D7aE2209A6B6",
        "native": "GLMR",
    },
    "42161": {
        "rpc": settings.arbitrum_rpc,
        "bridge_contract": "0x5a9673073ba5C0F52Aac535EC915D7aE2209A6B6",
        "native": "ETH",
    },
    "42220": {
        "rpc": settings.celo_rpc,
        "bridge_contract": "0x5a9673073ba5C0F52Aac535EC915D7aE2209A6B6",
        "native": "CELO",
    },
}
