"""Minimal deterministic backtest engine.

Long-only target-position model:
- signal[i] is decided using data up to and including bar i
- orders execute at bar i+1's OPEN with slippage and fees
- equity is marked to market at each bar close

The engine is fully deterministic: same code + data + config => same result.
The LLM is never involved in execution or metrics.
"""
import random
import uuid
from typing import Any

import pandas as pd

from ..schemas.backtest import BacktestConfig, BacktestResult, EquityPoint
from ..schemas.market_data import MarketDataset
from ..schemas.metrics import BacktestMetrics
from ..schemas.trade import Trade
from .data_normalization_service import DataValidationError
from .metrics_service import compute_metrics
from .strategy_sandbox import (
    StrategySandboxError,
    load_script_strategy,
    run_indicator_signals,
)


class ScriptContext:
    """Context handed to script strategies (`on_bar(ctx, bar)`)."""

    def __init__(self, params: dict[str, Any]) -> None:
        self.params = params
        self.position = 0
        self._target = 0
        self.state: dict[str, Any] = {}

    def buy(self) -> None:
        self._target = 1

    def sell(self) -> None:
        self._target = 0

    def target_position(self) -> int:
        return self._target


def _dataset_to_df(dataset: MarketDataset) -> pd.DataFrame:
    rows = [b.model_dump() for b in dataset.bars]
    df = pd.DataFrame(rows)
    df["timestamp"] = df["timestamp"].astype(str)
    return df


def _compute_signals(
    strategy_type: str,
    code: str,
    df: pd.DataFrame,
    params: dict[str, Any],
    logs: list[str],
) -> list[int]:
    if strategy_type == "indicator":
        return run_indicator_signals(code, df, params)

    strategy = load_script_strategy(code)
    ctx = ScriptContext(params)
    if hasattr(strategy, "on_start"):
        strategy.on_start(ctx)
    signals: list[int] = []
    for i in range(len(df)):
        bar = df.iloc[i].to_dict()
        result = None
        if hasattr(strategy, "on_bar"):
            result = strategy.on_bar(ctx, bar)
        if result is not None:
            target = 1 if int(result) > 0 else 0
            ctx._target = target
        target = ctx.target_position()
        if hasattr(strategy, "on_signal") and (not signals or target != signals[-1]):
            strategy.on_signal(ctx, {"index": i, "target": target})
        signals.append(target)
        ctx.position = target
    if hasattr(strategy, "on_stop"):
        strategy.on_stop(ctx)
    logs.append(f"script strategy produced {len(signals)} signals")
    return signals


def run_backtest(
    strategy: dict[str, Any],
    config: BacktestConfig,
    dataset: MarketDataset,
) -> BacktestResult:
    if not dataset.bars:
        raise DataValidationError("dataset has no bars; refusing to run backtest")
    if not (0 < config.position_size <= 1):
        raise ValueError("position_size must be in (0, 1]")

    random.seed(config.random_seed)
    logs: list[str] = []
    logs.append(
        f"data source: {dataset.meta.provider} ({dataset.meta.source})"
        + (" [MOCK DATA]" if dataset.meta.is_mock else "")
    )
    logs.append(
        f"bars: {len(dataset.bars)} | {config.symbol} {config.timeframe} "
        f"{config.start_date} -> {config.end_date}"
    )

    df = _dataset_to_df(dataset)
    params = {**strategy.get("parameters", {}), **config.parameters}
    signals = _compute_signals(
        strategy.get("strategy_type", "indicator"), strategy["code"], df, params, logs
    )

    cash = config.initial_capital
    quantity = 0.0
    bars_in_position = 0
    trades: list[Trade] = []
    equity_curve: list[EquityPoint] = []

    for i in range(len(df)):
        bar = df.iloc[i]
        # Execute yesterday's signal at today's open
        if i > 0:
            target = signals[i - 1]
            open_price = float(bar["open"])
            if target == 1 and quantity == 0:
                fill_price = open_price * (1 + config.slippage)
                equity_now = cash
                budget = equity_now * config.position_size
                fee = budget * config.fee_rate
                qty = (budget - fee) / fill_price
                if qty > 0:
                    cash -= qty * fill_price + fee
                    quantity = qty
                    trades.append(
                        Trade(
                            timestamp=str(bar["timestamp"]),
                            symbol=config.symbol,
                            side="buy",
                            quantity=round(qty, 6),
                            price=round(fill_price, 6),
                            fee=round(fee, 6),
                            reason=f"signal -> long at bar {i}",
                        )
                    )
                    logs.append(f"[{bar['timestamp']}] BUY {qty:.4f} @ {fill_price:.4f} fee {fee:.4f}")
            elif target == 0 and quantity > 0:
                fill_price = open_price * (1 - config.slippage)
                notional = quantity * fill_price
                fee = notional * config.fee_rate
                cash += notional - fee
                trades.append(
                    Trade(
                        timestamp=str(bar["timestamp"]),
                        symbol=config.symbol,
                        side="sell",
                        quantity=round(quantity, 6),
                        price=round(fill_price, 6),
                        fee=round(fee, 6),
                        reason=f"signal -> flat at bar {i}",
                    )
                )
                logs.append(f"[{bar['timestamp']}] SELL {quantity:.4f} @ {fill_price:.4f} fee {fee:.4f}")
                quantity = 0.0

        if quantity > 0:
            bars_in_position += 1
        equity = cash + quantity * float(bar["close"])
        equity_curve.append(EquityPoint(timestamp=str(bar["timestamp"]), equity=round(equity, 4)))

    final_equity = equity_curve[-1].equity if equity_curve else config.initial_capital
    metrics: BacktestMetrics = compute_metrics(
        equity_curve,
        trades,
        config.initial_capital,
        timeframe=config.timeframe,
        bars_in_position=bars_in_position,
        total_bars=len(df),
    )
    logs.append(
        f"final equity {final_equity:.2f} | return {metrics.total_return:.2%} | "
        f"max drawdown {metrics.max_drawdown:.2%} | trades {metrics.trade_count}"
    )

    return BacktestResult(
        backtest_id=uuid.uuid4().hex,
        strategy_id=config.strategy_id,
        symbol=config.symbol,
        timeframe=config.timeframe,
        start_date=config.start_date,
        end_date=config.end_date,
        initial_capital=config.initial_capital,
        final_equity=final_equity,
        metrics=metrics,
        equity_curve=equity_curve,
        trades=trades,
        logs=logs,
        data_source=dataset.meta.provider,
        is_mock_data=dataset.meta.is_mock,
        status="completed",
    )


__all__ = ["run_backtest", "StrategySandboxError", "DataValidationError"]
