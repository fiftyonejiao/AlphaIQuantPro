from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from .trade import Trade

PaperRunStatus = Literal["created", "running", "stopped", "failed", "completed"]
PaperRunMode = Literal["historical_replay", "mock_live", "exchange_paper_future"]


class PaperRunConfig(BaseModel):
    strategy_id: str
    symbol: str = "AAPL"
    timeframe: str = "1d"
    mode: PaperRunMode = "historical_replay"
    initial_capital: float = 100_000.0
    fee_rate: float = 0.001
    slippage: float = 0.0005
    position_size: float = 1.0
    lookback_days: int = 180
    replay_delay_seconds: float = 0.15
    parameters: dict[str, Any] = Field(default_factory=dict)


class PaperSignal(BaseModel):
    timestamp: str
    signal: int
    price: float
    note: str = ""


class PaperOrder(BaseModel):
    order_id: str
    timestamp: str
    symbol: str
    side: str
    quantity: float
    order_type: str = "market"
    status: str = "filled"


class PaperFill(BaseModel):
    order_id: str
    timestamp: str
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float


class OpenPosition(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    unrealized_pnl: float


class PaperRunState(BaseModel):
    run_id: str
    strategy_id: str
    status: PaperRunStatus
    mode: PaperRunMode
    symbol: str = ""
    timeframe: str = ""
    started_at: Optional[str] = None
    stopped_at: Optional[str] = None
    initial_capital: float = 0.0
    current_equity: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    open_positions: list[OpenPosition] = Field(default_factory=list)
    signals: list[PaperSignal] = Field(default_factory=list)
    orders: list[PaperOrder] = Field(default_factory=list)
    fills: list[PaperFill] = Field(default_factory=list)
    trades: list[Trade] = Field(default_factory=list)
    equity_curve: list[dict[str, Any]] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    logs: list[str] = Field(default_factory=list)
    data_source: str = "mock"
    is_mock_data: bool = True
    post_run_analysis: str = ""
