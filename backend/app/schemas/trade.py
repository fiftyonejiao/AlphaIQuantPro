from typing import Literal

from pydantic import BaseModel

TradeSide = Literal["buy", "sell"]


class Trade(BaseModel):
    timestamp: str
    symbol: str
    side: TradeSide
    quantity: float
    price: float
    fee: float
    reason: str = ""
