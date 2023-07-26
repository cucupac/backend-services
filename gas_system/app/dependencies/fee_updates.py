from app.settings import settings
from app.usecases.schemas.blockchain import AxChains

UPDATE_FEES_FREQUENCIES = {
    AxChains.ETHEREUM.value: settings.ethereum_update_frequency,
    AxChains.BSC.value: settings.binance_update_frequency,
    AxChains.POLYGON.value: settings.polygon_update_frequency,
    AxChains.AVALANCHE.value: settings.avalanche_update_frequency,
    AxChains.FANTOM.value: settings.fantom_update_frequency,
    AxChains.ARBITRUM.value: settings.arbitrum_update_frequency,
    AxChains.CELO.value: settings.celo_update_frequency,
}
