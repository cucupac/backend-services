from app.settings import settings
from app.usecases.schemas.blockchain import Chains

UPDATE_FEES_FREQUENCIES = {
    Chains.ETHEREUM.value: settings.ethereum_update_frequency,
    Chains.BSC.value: settings.binance_update_frequency,
    Chains.POLYGON.value: settings.polygon_update_frequency,
    Chains.AVALANCHE.value: settings.avalanche_update_frequency,
    Chains.FANTOM.value: settings.fantom_update_frequency,
    Chains.ARBITRUM.value: settings.arbitrum_update_frequency,
    Chains.CELO.value: settings.celo_update_frequency,
}
