import pytest

from app.schemas.backtest import BacktestConfig
from app.schemas.market_data import MarketDataMeta, MarketDataset
from app.services.backtest_engine import run_backtest
from app.services.data_normalization_service import DataValidationError, normalize_ohlcv
from app.services.market_data_service import generate_mock_ohlcv
from app.services.strategy_sandbox import StrategySandboxError, run_indicator_signals

MA_CODE = """
def generate_signals(df, params):
    fast = df["close"].rolling(int(params.get("fast_period", 5))).mean()
    slow = df["close"].rolling(int(params.get("slow_period", 20))).mean()
    return (fast > slow).astype(int).fillna(0)
"""

SCRIPT_CODE = """
class Strategy:
    def on_start(self, ctx):
        ctx.state["closes"] = []

    def on_bar(self, ctx, bar):
        closes = ctx.state["closes"]
        closes.append(bar["close"])
        if len(closes) < 10:
            return 0
        avg = sum(closes[-10:]) / 10
        return 1 if bar["close"] > avg else 0
"""


def _dataset(symbol="AAPL", start="2023-01-01", end="2024-01-01") -> MarketDataset:
    bars = normalize_ohlcv(generate_mock_ohlcv(symbol, "1d", start, end))
    meta = MarketDataMeta(
        provider="mock-generator", source="mock", symbol=symbol, timeframe="1d",
        retrieval_timestamp="2024-01-01T00:00:00+00:00", is_mock=True,
    )
    return MarketDataset(meta=meta, bars=bars)


def _config(**overrides) -> BacktestConfig:
    defaults = dict(
        strategy_id="s1", symbol="AAPL", timeframe="1d",
        start_date="2023-01-01", end_date="2024-01-01",
        initial_capital=100_000.0,
    )
    defaults.update(overrides)
    return BacktestConfig(**defaults)


def _strategy(code=MA_CODE, strategy_type="indicator"):
    return {"strategy_type": strategy_type, "code": code, "parameters": {}}


class TestBacktestEngine:
    def test_runs_indicator_strategy(self):
        result = run_backtest(_strategy(), _config(), _dataset())
        assert result.status == "completed"
        assert result.final_equity > 0
        assert len(result.equity_curve) > 200
        assert result.is_mock_data is True
        assert any("MOCK DATA" in log for log in result.logs)

    def test_is_deterministic(self):
        a = run_backtest(_strategy(), _config(), _dataset())
        b = run_backtest(_strategy(), _config(), _dataset())
        assert a.final_equity == b.final_equity
        assert [t.price for t in a.trades] == [t.price for t in b.trades]
        assert a.metrics.total_return == b.metrics.total_return

    def test_runs_script_strategy(self):
        result = run_backtest(
            _strategy(code=SCRIPT_CODE, strategy_type="script"), _config(), _dataset()
        )
        assert result.status == "completed"
        assert result.metrics.trade_count >= 0

    def test_trades_have_fees_and_reasons(self):
        result = run_backtest(_strategy(), _config(), _dataset())
        assert result.metrics.trade_count > 0
        for trade in result.trades:
            assert trade.fee > 0
            assert trade.reason

    def test_metrics_fields_present(self):
        result = run_backtest(_strategy(), _config(), _dataset())
        m = result.metrics
        assert m.max_drawdown >= 0
        assert 0 <= m.win_rate <= 1
        assert 0 <= m.exposure_time <= 1
        assert m.turnover >= 0
        assert m.cagr is not None  # 1-year range supports CAGR
        assert m.sharpe is not None  # enough daily points

    def test_refuses_empty_dataset(self):
        ds = _dataset()
        ds.bars = []
        with pytest.raises(DataValidationError):
            run_backtest(_strategy(), _config(), ds)

    def test_rejects_bad_position_size(self):
        with pytest.raises(ValueError):
            run_backtest(_strategy(), _config(position_size=0), _dataset())

    def test_broken_strategy_code_raises_sandbox_error(self):
        with pytest.raises(StrategySandboxError):
            run_backtest(_strategy(code="this is not python"), _config(), _dataset())


class TestSandbox:
    def test_dangerous_imports_blocked(self):
        code = """
import os
def generate_signals(df, params):
    return df["close"] * 0
"""
        import pandas as pd

        with pytest.raises(StrategySandboxError):
            run_indicator_signals(code, pd.DataFrame({"close": [1.0, 2.0]}), {})

    def test_allowed_imports_work(self):
        code = """
import math
def generate_signals(df, params):
    return (df["close"] > math.exp(0)).astype(int)
"""
        import pandas as pd

        signals = run_indicator_signals(code, pd.DataFrame({"close": [0.5, 2.0]}), {})
        assert signals == [0, 1]

    def test_signal_length_mismatch_rejected(self):
        code = """
def generate_signals(df, params):
    return [1]
"""
        import pandas as pd

        with pytest.raises(StrategySandboxError, match="length"):
            run_indicator_signals(code, pd.DataFrame({"close": [1.0, 2.0]}), {})
