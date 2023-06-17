from typing import Optional, List

from pydantic import BaseModel


class GasPrices(BaseModel):
    base_fee_per_gas_list: Optional[List[int]]
    max_priority_fee_per_gas_list: Optional[List[int]]
    gas_price_list: Optional[List[int]]
