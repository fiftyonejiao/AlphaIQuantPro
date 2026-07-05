"""Paper/simulation engine (NO real-money execution anywhere in MVP).

Runs a strategy against a historical replay or a mock live feed in a
background thread. Every signal, simulated order, and simulated fill is
recorded. Runs can be stopped by the user; a post-run analysis is generated
after stopping (deterministic summary + optional DeepSeek commentary).
"""
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import pandas as pd

from ..schemas.backtest import EquityPoint
from ..schemas.market_data import MarketDataset
from ..schemas.paper_run import (
    OpenPosition,
    PaperFill,
    PaperOrder,
    PaperRunConfig,
    PaperRunState,
    PaperSignal,
)
from ..schemas.trade import Trade
from .backtest_engine import ScriptContext
from .market_data_service import MarketDataService
from .metrics_service import compute_metrics
from .strategy_sandbox import load_script_strategy, run_indicator_signals


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class PaperRun:
    def __init__(self, config: PaperRunConfig, strategy: dict[str, Any]) -> None:
        self.config = config
        self.strategy = strategy
        self.state = PaperRunState(
            run_id=uuid.uuid4().hex,
            strategy_id=config.strategy_id,
            status="created",
            mode=config.mode,
            symbol=config.symbol,
            timeframe=config.timeframe,
            initial_capital=config.initial_capital,
            current_equity=config.initial_capital,
        )
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._cash = config.initial_capital
        self._quantity = 0.0
        self._avg_price = 0.0

    # -- lifecycle -----------------------------------------------------
    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self.state.status = "running"
        self.state.started_at = _utcnow_iso()
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def snapshot(self) -> PaperRunState:
        with self._lock:
            return self.state.model_copy(deep=True)

    # -- internals -----------------------------------------------------
    def _log(self, msg: str) -> None:
        self.state.logs.append(f"[{_utcnow_iso()}] {msg}")

    def _execute(self, side: str, price: float, timestamp: str, note: str) -> None:
        cfg = self.config
        order_id = uuid.uuid4().hex[:12]
        if side == "buy":
            fill_price = price * (1 + cfg.slippage)
            budget = self._cash * cfg.position_size
            fee = budget * cfg.fee_rate
            qty = (budget - fee) / fill_price
            if qty <= 0:
                return
            self._cash -= qty * fill_price + fee
            self._avg_price = fill_price
            self._quantity = qty
        else:
            fill_price = price * (1 - cfg.slippage)
            qty = self._quantity
            if qty <= 0:
                return
            notional = qty * fill_price
            fee = notional * cfg.fee_rate
            self._cash += notional - fee
            self.state.realized_pnl += qty * (fill_price - self._avg_price) - fee
            self._quantity = 0.0

        order = PaperOrder(
            order_id=order_id, timestamp=timestamp, symbol=cfg.symbol,
            side=side, quantity=round(qty, 6),
        )
        fill = PaperFill(
            order_id=order_id, timestamp=timestamp, symbol=cfg.symbol,
            side=side, quantity=round(qty, 6), price=round(fill_price, 6),
            fee=round(fee, 6),
        )
        trade = Trade(
            timestamp=timestamp, symbol=cfg.symbol, side=side,  # type: ignore[arg-type]
            quantity=round(qty, 6), price=round(fill_price, 6),
            fee=round(fee, 6), reason=note,
        )
        self.state.orders.append(order)
        self.state.fills.append(fill)
        self.state.trades.append(trade)
        self._log(f"{side.upper()} {qty:.4f} {cfg.symbol} @ {fill_price:.4f} (fee {fee:.4f})")

    def _mark(self, close: float, timestamp: str) -> None:
        unrealized = self._quantity * (close - self._avg_price) if self._quantity > 0 else 0.0
        equity = self._cash + self._quantity * close
        self.state.unrealized_pnl = round(unrealized, 4)
        self.state.current_equity = round(equity, 4)
        self.state.open_positions = (
            [OpenPosition(symbol=self.config.symbol, quantity=round(self._quantity, 6),
                          avg_price=round(self._avg_price, 6), unrealized_pnl=round(unrealized, 4))]
            if self._quantity > 0
            else []
        )
        self.state.equity_curve.append({"timestamp": timestamp, "equity": round(equity, 4)})

    def _fetch_dataset(self) -> MarketDataset:
        cfg = self.config
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=cfg.lookback_days)
        service = MarketDataService()
        return service.get_ohlcv(cfg.symbol, cfg.timeframe, start.isoformat(), end.isoformat())

    def _run(self) -> None:
        try:
            cfg = self.config
            dataset = self._fetch_dataset()
            source_label = f"{dataset.meta.provider} ({dataset.meta.source})"
            if dataset.meta.is_mock:
                source_label += " [MOCK DATA]"
            self.state.data_source = dataset.meta.provider
            self.state.is_mock_data = dataset.meta.is_mock
            mode_label = "historical replay" if cfg.mode == "historical_replay" else "mock live feed"
            self._log(f"paper run started | mode: {mode_label} | data: {source_label}")
            self._log("SIMULATION ONLY — no real orders are ever sent")

            rows = [b.model_dump() for b in dataset.bars]
            df = pd.DataFrame(rows)
            params = {**self.strategy.get("parameters", {}), **cfg.parameters}

            strategy_type = self.strategy.get("strategy_type", "indicator")
            script = None
            ctx = None
            if strategy_type == "script":
                script = load_script_strategy(self.strategy["code"])
                ctx = ScriptContext(params)
                if hasattr(script, "on_start"):
                    script.on_start(ctx)

            prev_target = 0
            for i in range(len(df)):
                if self._stop_event.is_set():
                    break
                bar = df.iloc[i]
                ts = str(bar["timestamp"])
                close = float(bar["close"])

                if strategy_type == "indicator":
                    window = df.iloc[: i + 1]
                    signals = run_indicator_signals(self.strategy["code"], window, params)
                    target = signals[-1]
                else:
                    result = script.on_bar(ctx, bar.to_dict()) if hasattr(script, "on_bar") else None
                    if result is not None:
                        ctx._target = 1 if int(result) > 0 else 0
                    target = ctx.target_position()
                    ctx.position = target

                with self._lock:
                    if target != prev_target:
                        self.state.signals.append(
                            PaperSignal(timestamp=ts, signal=target, price=close,
                                        note="long" if target == 1 else "flat")
                        )
                        if target == 1 and self._quantity == 0:
                            self._execute("buy", close, ts, "signal -> long")
                        elif target == 0 and self._quantity > 0:
                            self._execute("sell", close, ts, "signal -> flat")
                        prev_target = target
                    self._mark(close, ts)

                time.sleep(cfg.replay_delay_seconds)

            with self._lock:
                if script is not None and hasattr(script, "on_stop"):
                    script.on_stop(ctx)
                stopped_by_user = self._stop_event.is_set()
                self.state.status = "stopped" if stopped_by_user else "completed"
                self.state.stopped_at = _utcnow_iso()
                self._log(
                    "run stopped by user" if stopped_by_user else "replay completed"
                )
                eq_points = [EquityPoint(**p) for p in self.state.equity_curve]
                trades = self.state.trades
                metrics = compute_metrics(
                    eq_points, trades, cfg.initial_capital, timeframe=cfg.timeframe,
                    bars_in_position=sum(1 for _ in self.state.open_positions),
                    total_bars=len(eq_points),
                )
                self.state.metrics = metrics.model_dump()
        except Exception as exc:  # noqa: BLE001
            with self._lock:
                self.state.status = "failed"
                self.state.stopped_at = _utcnow_iso()
                self._log(f"run failed: {type(exc).__name__}: {exc}")


class PaperRunManager:
    """In-memory registry of active runs; finished runs persist to the DB."""

    def __init__(self) -> None:
        self._runs: dict[str, PaperRun] = {}
        self._lock = threading.Lock()

    def start_run(self, config: PaperRunConfig, strategy: dict[str, Any]) -> PaperRunState:
        run = PaperRun(config, strategy)
        with self._lock:
            self._runs[run.state.run_id] = run
        run.start()
        return run.snapshot()

    def get(self, run_id: str) -> Optional[PaperRun]:
        with self._lock:
            return self._runs.get(run_id)

    def stop_run(self, run_id: str) -> Optional[PaperRunState]:
        run = self.get(run_id)
        if run is None:
            return None
        run.stop()
        if run._thread is not None:
            run._thread.join(timeout=30)
        return run.snapshot()

    def all_states(self) -> list[PaperRunState]:
        with self._lock:
            return [r.snapshot() for r in self._runs.values()]


paper_run_manager = PaperRunManager()
