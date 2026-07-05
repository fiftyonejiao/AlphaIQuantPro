from typing import Any, Optional

from pydantic import BaseModel, Field

from .metrics import BacktestMetrics
from .trade import Trade


class EquityPoint(BaseModel):
    timestamp: str
    equity: float


class BacktestConfig(BaseModel):
    strategy_id: str
    symbol: str = "AAPL"
    timeframe: str = "1d"
    start_date: str
    end_date: str
    initial_capital: float = 100_000.0
    fee_rate: float = 0.001
    slippage: float = 0.0005
    position_size: float = Field(default=1.0, description="Fraction of equity per position (0-1]")
    parameters: dict[str, Any] = Field(default_factory=dict)
    random_seed: int = 42


class BacktestResult(BaseModel):
    backtest_id: str
    strategy_id: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    initial_capital: float
    final_equity: float
    metrics: BacktestMetrics
    equity_curve: list[EquityPoint]
    trades: list[Trade]
    logs: list[str]
    data_source: str = "mock"
    is_mock_data: bool = True
    status: str = "completed"
    created_at: str = ""
    error: Optional[str] = None


class BacktestSummary(BaseModel):
    backtest_id: str
    strategy_id: str
    strategy_name: str = ""
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    status: str
    total_return: float = 0.0
    max_drawdown: float = 0.0
    trade_count: int = 0
    is_mock_data: bool = True
    created_at: str = ""
