# AlphaQuantPro — Strategy Spec

Two strategy styles are supported. Both run in a restricted local sandbox
(curated builtins; only `pandas`, `numpy`, `math` importable). This is a
convenience sandbox for a local, single-user MVP — do not run untrusted code.

## 1. Indicator strategy (DataFrame-based)

Define `generate_signals(df, params)`:

- `df`: pandas DataFrame with columns `timestamp, open, high, low, close, volume`.
- `params`: dict of strategy parameters (from the strategy record, overridable per backtest).
- Return: pandas Series (or list) of target positions per bar — `1` = long, `0` = flat. Length must equal `len(df)`.

```python
def generate_signals(df, params):
    fast = df["close"].rolling(int(params.get("fast_period", 10))).mean()
    slow = df["close"].rolling(int(params.get("slow_period", 30))).mean()
    return (fast > slow).astype(int).fillna(0)
```

## 2. Script strategy (event-driven)

Define a `Strategy` class. Supported hooks:

- `on_start(ctx)` — called once before the run.
- `on_bar(ctx, bar)` — called per bar; `bar` is a dict with OHLCV fields. Return `1` (long) / `0` (flat), or call `ctx.buy()` / `ctx.sell()`.
- `on_signal(ctx, signal)` — called when the target position changes.
- `on_stop(ctx)` — called once after the run.

`ctx` provides: `ctx.params` (dict), `ctx.position` (current target), `ctx.state` (scratch dict), `ctx.buy()`, `ctx.sell()`.

```python
class Strategy:
    def on_start(self, ctx):
        ctx.state["closes"] = []

    def on_bar(self, ctx, bar):
        closes = ctx.state["closes"]
        closes.append(bar["close"])
        if len(closes) < 20:
            return 0
        return 1 if bar["close"] > sum(closes[-20:]) / 20 else 0
```

## Execution model

- Long-only, single position, target-position semantics.
- Signal decided on bar `i` executes at bar `i+1` open (backtest) with slippage and fees.
- Position sizing: fraction of current equity (`position_size` in (0, 1]).

## Constraints

- No file/network/OS access inside strategy code.
- No lookahead protection beyond next-bar execution — avoid using future rows in indicator code.
- Signals other than 0/1 are clamped (`>0` → 1, else 0).
