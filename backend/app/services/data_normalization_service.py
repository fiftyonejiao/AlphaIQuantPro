"""Normalize raw provider payloads into deterministic internal schemas.

The backtest and paper/simulation engines refuse to consume anything that
has not passed through this validation layer.
"""
from datetime import datetime, timezone
from typing import Any

from ..schemas.market_data import OHLCVBar

REQUIRED_FIELDS = ("timestamp", "open", "high", "low", "close", "volume")


class DataValidationError(ValueError):
    """Raised when market data is missing fields or malformed."""


def _parse_timestamp(value: Any) -> str:
    if isinstance(value, (int, float)):
        # epoch seconds or milliseconds
        ts = float(value)
        if ts > 1e12:
            ts /= 1000.0
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise DataValidationError(f"invalid timestamp: {value!r}") from exc
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    raise DataValidationError(f"unsupported timestamp type: {type(value).__name__}")


def normalize_ohlcv(raw_bars: list[dict[str, Any]]) -> list[OHLCVBar]:
    """Validate and normalize raw OHLCV rows.

    Raises DataValidationError for missing fields, non-numeric values,
    inconsistent high/low, or non-positive prices.
    """
    if not raw_bars:
        raise DataValidationError("empty OHLCV payload")

    bars: list[OHLCVBar] = []
    for i, row in enumerate(raw_bars):
        missing = [f for f in REQUIRED_FIELDS if f not in row or row[f] is None]
        if missing:
            raise DataValidationError(f"bar {i}: missing fields {missing}")
        try:
            o = float(row["open"])
            h = float(row["high"])
            low = float(row["low"])
            c = float(row["close"])
            v = float(row["volume"])
        except (TypeError, ValueError) as exc:
            raise DataValidationError(f"bar {i}: non-numeric OHLCV value") from exc
        if min(o, h, low, c) <= 0:
            raise DataValidationError(f"bar {i}: non-positive price")
        if v < 0:
            raise DataValidationError(f"bar {i}: negative volume")
        if h < max(o, c) or low > min(o, c) or h < low:
            raise DataValidationError(f"bar {i}: inconsistent high/low range")
        bars.append(
            OHLCVBar(
                timestamp=_parse_timestamp(row["timestamp"]),
                open=o,
                high=h,
                low=low,
                close=c,
                volume=v,
            )
        )

    bars.sort(key=lambda b: b.timestamp)
    seen: set[str] = set()
    deduped: list[OHLCVBar] = []
    for bar in bars:
        if bar.timestamp in seen:
            continue
        seen.add(bar.timestamp)
        deduped.append(bar)
    return deduped
