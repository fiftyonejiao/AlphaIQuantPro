from typing import Optional

from pydantic import BaseModel


class BacktestMetrics(BaseModel):
    total_return: float = 0.0
    cagr: Optional[float] = None
    max_drawdown: float = 0.0
    sharpe: Optional[float] = None
    win_rate: float = 0.0
    profit_factor: Optional[float] = None
    trade_count: int = 0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    exposure_time: float = 0.0
    turnover: float = 0.0
