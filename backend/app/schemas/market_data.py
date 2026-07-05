"""Deterministic internal market-data schemas.

Every dataset consumed by the backtest or paper/simulation engine must pass
through these schemas. Raw provider payloads are never consumed directly.
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field

DataSourceKind = Literal["qveris", "mock"]


class OHLCVBar(BaseModel):
    timestamp: str = Field(description="ISO-8601 bar open timestamp (UTC)")
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketDataMeta(BaseModel):
    provider: str
    source: DataSourceKind
    capability_id: Optional[str] = None
    symbol: str
    market: str = "stocks"
    timeframe: str
    currency: str = "USD"
    source_timestamp: Optional[str] = None
    retrieval_timestamp: str
    quality_notes: list[str] = Field(default_factory=list)
    is_mock: bool = False


class MarketDataset(BaseModel):
    meta: MarketDataMeta
    bars: list[OHLCVBar]


class Quote(BaseModel):
    symbol: str
    price: float
    timestamp: str
    source: DataSourceKind
    is_mock: bool = False


class MarketDataStatus(BaseModel):
    qveris_configured: bool
    qveris_reachable: bool
    active_source: DataSourceKind
    session_id: str
    notes: list[str] = Field(default_factory=list)


class FetchRequest(BaseModel):
    symbol: str
    timeframe: str = "1d"
    start_date: str
    end_date: str
    market: str = "stocks"
