"""Market data access layer.

QVeris.ai is the primary (and only real) data gateway. It uses the QVeris
Discover -> Inspect -> Call workflow to fetch OHLCV bars and quotes from real
providers, normalizing every response into deterministic internal schemas.

When the QVeris key is missing or a call fails, we fall back to explicitly
labeled MOCK DATA — a deterministic seeded random walk so backtests remain
reproducible. The LLM never produces market data.
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
from .qveris_client import QverisClient

OHLCV_QUERY = "historical end of day daily OHLCV stock price bars for equities"
QUOTE_QUERY = "real-time stock quote latest price for equities"

# Common field-name aliases across providers (Tiingo, FMP, EODHD, etc.).
_SYMBOL_KEYS = ("symbol", "ticker", "symbols", "code", "instrument")
_DATE_RANGE_KEYS = (("from", "to"), ("start_date", "end_date"), ("startDate", "endDate"), ("start", "end"))
_INTERVAL_KEYS = ("interval", "resolution", "period", "timeframe", "frequency")

_TS_FIELDS = ("timestamp", "date", "datetime", "time", "t", "day")
_OPEN_FIELDS = ("open", "adjOpen", "o", "adj_open")
_HIGH_FIELDS = ("high", "adjHigh", "h", "adj_high")
_LOW_FIELDS = ("low", "adjLow", "l", "adj_low")
_CLOSE_FIELDS = ("close", "adjClose", "c", "adj_close", "price")
_VOLUME_FIELDS = ("volume", "adjVolume", "v", "vol", "adj_volume")


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


def _pick(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for k in keys:
        if k in row and row[k] is not None:
            return row[k]
    return None


def _map_qveris_rows(data: Any) -> list[dict[str, Any]]:
    """Map an arbitrary provider payload into raw OHLCV rows (pre-normalization)."""
    rows: Any = data
    if isinstance(data, dict):
        # Some providers wrap the series in a key such as results/data/bars/prices.
        for key in ("results", "data", "bars", "prices", "candles", "historical", "values"):
            if isinstance(data.get(key), list):
                rows = data[key]
                break
        else:
            rows = [data]
    if not isinstance(rows, list):
        return []

    mapped: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        ts = _pick(row, _TS_FIELDS)
        o = _pick(row, _OPEN_FIELDS)
        h = _pick(row, _HIGH_FIELDS)
        low = _pick(row, _LOW_FIELDS)
        c = _pick(row, _CLOSE_FIELDS)
        v = _pick(row, _VOLUME_FIELDS)
        if ts is None or None in (o, h, low, c):
            continue
        mapped.append(
            {
                "timestamp": ts,
                "open": o,
                "high": h,
                "low": low,
                "close": c,
                "volume": v if v is not None else 0.0,
            }
        )
    return mapped


def _has_range_params(param_names: list[str]) -> bool:
    names = set(param_names)
    if any(sk in names and ek in names for sk, ek in _DATE_RANGE_KEYS):
        return True
    return any(k in names for k in ("from", "start_date", "startDate", "start"))


def _build_params(
    param_names: list[str], symbol: str, start_date: str, end_date: str, timeframe: str
) -> dict[str, Any]:
    names = set(param_names)
    params: dict[str, Any] = {}

    for k in _SYMBOL_KEYS:
        if k in names:
            params[k] = symbol
            break
    else:
        params["symbol"] = symbol

    for start_key, end_key in _DATE_RANGE_KEYS:
        if start_key in names:
            params[start_key] = start_date
        if end_key in names:
            params[end_key] = end_date

    if timeframe != "1d":
        for k in _INTERVAL_KEYS:
            if k in names:
                params[k] = timeframe
                break
    return params


class MarketDataService:
    def __init__(self, client: Optional[QverisClient] = None) -> None:
        self.client = client or QverisClient()

    def _fetch_via_qveris(
        self, symbol: str, timeframe: str, start_date: str, end_date: str, market: str
    ) -> Optional[MarketDataset]:
        """Try the real QVeris Discover -> Inspect -> Call flow. None on failure.

        Prefers capabilities that expose a date-range so a full historical
        series is returned (needed for backtests), not just the latest bar.
        """
        discovery = self.client.discover(OHLCV_QUERY, limit=12)
        if not discovery.capabilities:
            return None

        # Rank date-range-capable tools first so we get a full series.
        ranked = sorted(
            discovery.capabilities,
            key=lambda c: 0 if _has_range_params(c.params) else 1,
        )
        range_requested = start_date != end_date and start_date and end_date
        min_bars = 2 if range_requested else 1
        best_single: Optional[MarketDataset] = None

        def _to_dataset(cap, result, bars) -> MarketDataset:
            return MarketDataset(
                meta=MarketDataMeta(
                    provider=cap.provider or "qveris",
                    source="qveris",
                    capability_id=cap.tool_id,
                    symbol=symbol,
                    market=market,
                    timeframe=timeframe,
                    currency="USD",
                    source_timestamp=None,
                    retrieval_timestamp=_utcnow_iso(),
                    quality_notes=[
                        f"QVeris tool {cap.tool_id}",
                        f"execution {result.execution_id} · cost {result.cost}",
                        f"{len(bars)} bars normalized",
                    ],
                    is_mock=False,
                ),
                bars=bars,
            )

        for cap in ranked[:6]:
            params = _build_params(cap.params, symbol, start_date, end_date, timeframe)
            result = self.client.call(cap.tool_id, params, search_id=discovery.search_id)
            if not result.ok or result.data is None:
                continue
            raw = _map_qveris_rows(result.data)
            if len(raw) < 1:
                continue
            try:
                bars = normalize_ohlcv(raw)
            except DataValidationError:
                continue
            if len(bars) >= min_bars:
                return _to_dataset(cap, result, bars)
            if best_single is None:
                best_single = _to_dataset(cap, result, bars)

        # Only single-bar tools responded; prefer real data over mock.
        return best_single

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str,
        market: str = "stocks",
    ) -> MarketDataset:
        quality_notes: list[str] = []

        if self.client.is_configured:
            try:
                dataset = self._fetch_via_qveris(symbol, timeframe, start_date, end_date, market)
                if dataset is not None:
                    return dataset
                quality_notes.append("no usable OHLCV capability returned by QVeris")
            except Exception as exc:  # noqa: BLE001
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
                discovery = self.client.discover(QUOTE_QUERY, limit=5)
                for cap in discovery.capabilities[:3]:
                    params = _build_params(cap.params, symbol, "", "", "1d")
                    result = self.client.call(cap.tool_id, params, search_id=discovery.search_id)
                    if result.ok and result.data is not None:
                        rows = _map_qveris_rows(result.data)
                        if rows:
                            last = rows[-1]
                            return Quote(
                                symbol=symbol,
                                price=float(last["close"]),
                                timestamp=str(last["timestamp"]),
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
        active = "qveris" if qveris_status.configured and qveris_status.reachable else "mock"
        return MarketDataStatus(
            qveris_configured=qveris_status.configured,
            qveris_reachable=qveris_status.reachable,
            active_source=active,
            session_id=settings.qveris_session_id,
            notes=[qveris_status.message] if qveris_status.message else [],
        )

    def get_sources(self) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []
        if self.client.is_configured:
            try:
                discovery = self.client.discover(OHLCV_QUERY, limit=10)
                for cap in discovery.capabilities:
                    sources.append(
                        {
                            "capability_id": cap.tool_id,
                            "name": cap.name,
                            "category": "market_data",
                            "description": cap.description,
                            "provider": cap.provider,
                        }
                    )
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
