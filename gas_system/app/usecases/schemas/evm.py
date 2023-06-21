from typing import List, Optional

from pydantic import BaseModel, Field


class GasPrices(BaseModel):
    base_fee_per_gas_list: Optional[List[int]] = Field(
        None,
        description="A list baseFeePerGas amounts for a desired number of blocks. List length varies depending on desired block count.",
        example=[25e9, 26e9, 25e9],
    )
    max_priority_fee_per_gas_list: Optional[List[int]] = Field(
        None,
        description="A list maxPriorityFeePerGas amounts for a desired number of blocks. List length varies depending on desired block count.",
        example=[10e9, 11e9, 12e9],
    )
    gas_price_list: Optional[List[int]] = Field(
        None,
        description="A list of median gas prices per block. List length varies depending on desired block count.",
        example=[25e9, 26e9, 25e9],
    )
