"""Post-run analysis: deterministic summary first, optional DeepSeek commentary."""
from typing import Any, Optional

from .llm_service import LLMService


def deterministic_summary(state: dict[str, Any]) -> str:
    metrics = state.get("metrics", {}) or {}
    lines = [
        f"Run {state.get('run_id', '')[:8]} | strategy {state.get('strategy_id', '')[:8]} | "
        f"mode {state.get('mode')} | status {state.get('status')}",
        f"Symbol {state.get('symbol')} {state.get('timeframe')} | data source: "
        f"{state.get('data_source')}{' [MOCK DATA]' if state.get('is_mock_data') else ''}",
        f"Initial capital {state.get('initial_capital', 0):,.2f} -> "
        f"final equity {state.get('current_equity', 0):,.2f}",
        f"Realized PnL {state.get('realized_pnl', 0):,.2f} | "
        f"unrealized PnL {state.get('unrealized_pnl', 0):,.2f}",
        f"Signals {len(state.get('signals', []))} | orders {len(state.get('orders', []))} | "
        f"fills {len(state.get('fills', []))}",
    ]
    if metrics:
        lines.append(
            f"Total return {metrics.get('total_return', 0):.2%} | "
            f"max drawdown {metrics.get('max_drawdown', 0):.2%} | "
            f"win rate {metrics.get('win_rate', 0):.2%} | trades {metrics.get('trade_count', 0)}"
        )
    return "\n".join(lines)


def generate_post_run_analysis(
    state: dict[str, Any],
    language: str = "en",
    llm: Optional[LLMService] = None,
) -> dict[str, Any]:
    summary = deterministic_summary(state)
    llm = llm or LLMService()
    slim_state = {
        "status": state.get("status"),
        "mode": state.get("mode"),
        "symbol": state.get("symbol"),
        "initial_capital": state.get("initial_capital"),
        "current_equity": state.get("current_equity"),
        "realized_pnl": state.get("realized_pnl"),
        "metrics": state.get("metrics"),
        "trades": state.get("trades", [])[:50],
        "signals": state.get("signals", [])[:50],
    }
    ai = llm.generate_run_analysis(slim_state, language=language)
    return {
        "deterministic_summary": summary,
        "ai_analysis": ai.text,
        "ai_is_mock": ai.is_mock,
        "disclaimer": "Not financial advice. Simulated results do not guarantee future performance.",
    }
