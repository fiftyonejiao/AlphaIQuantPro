"""Deterministic performance metrics. No LLM involvement — ever."""
import math
from datetime import datetime
from typing import Optional

from ..schemas.backtest import EquityPoint
from ..schemas.metrics import BacktestMetrics
from ..schemas.trade import Trade

TRADING_PERIODS_PER_YEAR = {"1d": 252, "1h": 252 * 6.5, "15m": 252 * 26}


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def compute_round_trip_pnls(trades: list[Trade]) -> list[float]:
    """Pair buys/sells (FIFO within a long-only model) into round-trip PnLs."""
    pnls: list[float] = []
    open_qty = 0.0
    open_cost = 0.0
    for t in trades:
        if t.side == "buy":
            open_cost += t.quantity * t.price + t.fee
            open_qty += t.quantity
        else:
            if open_qty <= 0:
                continue
            qty = min(t.quantity, open_qty)
            avg_cost = open_cost / open_qty
            pnls.append(qty * t.price - t.fee - qty * avg_cost)
            open_cost -= qty * avg_cost
            open_qty -= qty
    return pnls


def compute_metrics(
    equity_curve: list[EquityPoint],
    trades: list[Trade],
    initial_capital: float,
    timeframe: str = "1d",
    bars_in_position: int = 0,
    total_bars: int = 0,
) -> BacktestMetrics:
    metrics = BacktestMetrics()
    if not equity_curve:
        return metrics

    equities = [p.equity for p in equity_curve]
    final_equity = equities[-1]
    metrics.total_return = (final_equity / initial_capital) - 1.0 if initial_capital > 0 else 0.0

    # Max drawdown
    peak = equities[0]
    max_dd = 0.0
    for eq in equities:
        peak = max(peak, eq)
        if peak > 0:
            max_dd = max(max_dd, (peak - eq) / peak)
    metrics.max_drawdown = max_dd

    # CAGR — only when the date range spans enough time (>= ~30 days)
    try:
        span_days = (_parse(equity_curve[-1].timestamp) - _parse(equity_curve[0].timestamp)).days
        if span_days >= 30 and initial_capital > 0 and final_equity > 0:
            years = span_days / 365.25
            metrics.cagr = (final_equity / initial_capital) ** (1.0 / years) - 1.0
    except (ValueError, OverflowError):
        metrics.cagr = None

    # Sharpe (annualized, rf=0) — needs enough return points
    returns = [
        (equities[i] / equities[i - 1]) - 1.0
        for i in range(1, len(equities))
        if equities[i - 1] > 0
    ]
    if len(returns) >= 20:
        mean_r = sum(returns) / len(returns)
        var = sum((r - mean_r) ** 2 for r in returns) / (len(returns) - 1)
        std = math.sqrt(var)
        if std > 1e-12:
            periods = TRADING_PERIODS_PER_YEAR.get(timeframe, 252)
            metrics.sharpe = (mean_r / std) * math.sqrt(periods)

    # Trade statistics from round-trip PnLs
    pnls = compute_round_trip_pnls(trades)
    metrics.trade_count = len(trades)
    if pnls:
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]
        metrics.win_rate = len(wins) / len(pnls)
        metrics.avg_win = sum(wins) / len(wins) if wins else 0.0
        metrics.avg_loss = sum(losses) / len(losses) if losses else 0.0
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        metrics.profit_factor = (gross_profit / gross_loss) if gross_loss > 1e-12 else None

    if total_bars > 0:
        metrics.exposure_time = bars_in_position / total_bars

    traded_notional = sum(t.quantity * t.price for t in trades)
    avg_equity = sum(equities) / len(equities)
    metrics.turnover = traded_notional / avg_equity if avg_equity > 0 else 0.0

    return metrics


def sharpe_is_available(metrics: BacktestMetrics) -> Optional[float]:
    return metrics.sharpe
