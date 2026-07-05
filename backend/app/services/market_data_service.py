"""Market data access layer.

QVeris.ai is the primary (and only real) data gateway. When the QVeris key
is missing or a call fails, we fall back to explicitly labeled MOCK DATA —
a deterministic seeded random walk so backtests remain reproducible.
The LLM never produces market data.
"""
import hashlib
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from ..config import get_settings
from ..schemas.market_data import (
    MarketDataMeta,
    MarketDataset,
    MarketDataStatus,
    OHLCVBar,
    Quote,
)
from .data_normalization_service import DataValidationError, normalize_ohlcv
from .qveris_client import QverisClient, QverisNotConfiguredError

OHLCV_CAPABILITY_HINT = "market_data.ohlcv"
QUOTE_CAPABILITY_HINT = "market_data.quote"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _seed_for(symbol: str, timeframe: str) -> int:
    digest = hashlib.sha256(f"{symbol}:{timeframe}".encode()).hexdigest()
    return int(digest[:8], 16)


def generate_mock_ohlcv(
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    """Deterministic mock OHLCV bars (seeded random walk). Clearly mock."""
    start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
    if end <= start:
        raise DataValidationError("end_date must be after start_date")

    step = {"1d": timedelta(days=1), "1h": timedelta(hours=1), "15m": timedelta(minutes=15)}.get(
        timeframe, timedelta(days=1)
    )
    rng = random.Random(_seed_for(symbol, timeframe))
    price = 50.0 + (rng.random() * 200.0)
    bars: list[dict[str, Any]] = []
    ts = start
    while ts <= end:
        if timeframe == "1d" and ts.weekday() >= 5:
            ts += step
            continue
        drift = rng.gauss(0.0004, 0.018)
        open_p = price
        close_p = max(1.0, open_p * (1.0 + drift))
        high_p = max(open_p, close_p) * (1.0 + abs(rng.gauss(0, 0.006)))
        low_p = min(open_p, close_p) * (1.0 - abs(rng.gauss(0, 0.006)))
        volume = round(1_000_000 * (0.5 + rng.random()), 0)
        bars.append(
            {
                "timestamp": ts.isoformat(),
                "open": round(open_p, 4),
                "high": round(high_p, 4),
                "low": round(low_p, 4),
                "close": round(close_p, 4),
                "volume": volume,
            }
        )
        price = close_p
        ts += step
    return bars


class MarketDataService:
    def __init__(self, client: Optional[QverisClient] = None) -> None:
        self.client = client or QverisClient()

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str,
        market: str = "stocks",
    ) -> MarketDataset:
        quality_notes: list[str] = []
        capability_id: Optional[str] = None

        if self.client.is_configured:
            try:
                capabilities = self.client.discover(category="market_data")
                ohlcv_caps = [
                    c
                    for c in capabilities
                    if "ohlcv" in c.capability_id.lower() or "ohlcv" in c.name.lower()
                ]
                if ohlcv_caps:
                    capability_id = ohlcv_caps[0].capability_id
                    self.client.inspect(capability_id)
                    result = self.client.call(
                        capability_id,
                        {
                            "symbol": symbol,
                            "timeframe": timeframe,
                            "start_date": start_date,
                            "end_date": end_date,
                            "market": market,
                        },
                    )
                    if result.ok and isinstance(result.data, dict):
                        raw_bars = result.data.get("bars", [])
                        bars = normalize_ohlcv(raw_bars)
                        meta = MarketDataMeta(
                            provider="qveris",
                            source="qveris",
                            capability_id=capability_id,
                            symbol=symbol,
                            market=market,
                            timeframe=timeframe,
                            currency=str(result.data.get("currency", "USD")),
                            source_timestamp=result.data.get("as_of"),
                            retrieval_timestamp=_utcnow_iso(),
                            quality_notes=quality_notes,
                            is_mock=False,
                        )
                        return MarketDataset(meta=meta, bars=bars)
                    quality_notes.append(f"qveris call failed: {result.error}")
                else:
                    quality_notes.append("no OHLCV capability discovered on QVeris")
            except (QverisNotConfiguredError, DataValidationError, Exception) as exc:  # noqa: BLE001
                quality_notes.append(f"qveris error: {type(exc).__name__}")
        else:
            quality_notes.append("QVERIS_API_KEY missing")

        # Explicit mock fallback — clearly labeled MOCK DATA everywhere.
        quality_notes.append("MOCK DATA: deterministic seeded random walk")
        raw = generate_mock_ohlcv(symbol, timeframe, start_date, end_date)
        bars = normalize_ohlcv(raw)
        meta = MarketDataMeta(
            provider="mock-generator",
            source="mock",
            capability_id=None,
            symbol=symbol,
            market=market,
            timeframe=timeframe,
            currency="USD",
            source_timestamp=None,
            retrieval_timestamp=_utcnow_iso(),
            quality_notes=quality_notes,
            is_mock=True,
        )
        return MarketDataset(meta=meta, bars=bars)

    def get_quote(self, symbol: str) -> Quote:
        if self.client.is_configured:
            try:
                capabilities = self.client.discover(category="market_data")
                quote_caps = [c for c in capabilities if "quote" in c.capability_id.lower()]
                if quote_caps:
                    result = self.client.call(quote_caps[0].capability_id, {"symbol": symbol})
                    if result.ok and isinstance(result.data, dict):
                        return Quote(
                            symbol=symbol,
                            price=float(result.data.get("price", 0.0)),
                            timestamp=str(result.data.get("timestamp", _utcnow_iso())),
                            source="qveris",
                            is_mock=False,
                        )
            except Exception:  # noqa: BLE001
                pass
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=10)
        bars = generate_mock_ohlcv(symbol, "1d", start.date().isoformat(), end.date().isoformat())
        return Quote(
            symbol=symbol,
            price=bars[-1]["close"],
            timestamp=_utcnow_iso(),
            source="mock",
            is_mock=True,
        )

    def get_status(self) -> MarketDataStatus:
        settings = get_settings()
        qveris_status = self.client.status()
        return MarketDataStatus(
            qveris_configured=qveris_status.configured,
            qveris_reachable=qveris_status.reachable,
            active_source="qveris" if qveris_status.configured and qveris_status.reachable else "mock",
            session_id=settings.qveris_session_id,
            notes=[qveris_status.message] if qveris_status.message else [],
        )

    def get_sources(self) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []
        if self.client.is_configured:
            try:
                for cap in self.client.discover():
                    sources.append(cap.model_dump())
            except Exception:  # noqa: BLE001
                pass
        if not sources:
            sources.append(
                {
                    "capability_id": "mock.ohlcv",
                    "name": "Mock OHLCV Generator (MOCK DATA)",
                    "category": "market_data",
                    "description": "Deterministic seeded random walk used when QVeris is not configured.",
                    "provider": "mock-generator",
                }
            )
        return sources


def bars_to_rows(bars: list[OHLCVBar]) -> list[dict[str, Any]]:
    return [b.model_dump() for b in bars]
