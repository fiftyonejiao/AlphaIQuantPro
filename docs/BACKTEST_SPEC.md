# AlphaQuantPro — Backtest Spec

## Engine guarantees

- **Deterministic**: same strategy code + data + config → identical results. Mock data is seeded by symbol/timeframe. `random_seed` is applied before each run.
- **Auditable**: every fill is logged with timestamp, side, quantity, price, and fee; run logs record the data source (including `MOCK DATA` labeling).
- **Validated inputs**: the engine refuses to run on missing/malformed OHLCV (normalization layer raises before execution).
- **No LLM involvement**: execution and metrics are pure deterministic computation.

## Config

| Field | Default | Notes |
| --- | --- | --- |
| `symbol` | `AAPL` | Any symbol (mock generator is symbol-seeded) |
| `timeframe` | `1d` | `1d`, `1h`, `15m` |
| `start_date` / `end_date` | — | ISO dates; end must be after start |
| `initial_capital` | `100000` | |
| `fee_rate` | `0.001` | Applied to notional on each fill |
| `slippage` | `0.0005` | Buy fills at `open*(1+s)`, sell at `open*(1-s)` |
| `position_size` | `1.0` | Fraction of equity per entry, in (0, 1] |
| `parameters` | `{}` | Merged over the strategy's stored parameters |
| `random_seed` | `42` | For any stochastic strategy logic |

## Execution model

1. Bars are normalized and sorted; the strategy produces a target position per bar (1 long / 0 flat).
2. The signal from bar `i` is executed at bar `i+1`'s open (reduces lookahead).
3. Equity is marked to market at each bar close: `cash + quantity * close`.

## Metrics

| Metric | Definition |
| --- | --- |
| Total return | `final_equity / initial_capital - 1` |
| CAGR | Annualized; only when the range spans ≥ 30 days |
| Max drawdown | Max peak-to-trough equity decline |
| Sharpe | Annualized mean/std of per-bar returns (rf = 0); needs ≥ 20 return points |
| Win rate | Winning round-trips / total round-trips (FIFO pairing) |
| Profit factor | Gross profit / gross loss (null when no losses) |
| Trade count | Number of fills |
| Avg win / avg loss | Mean round-trip PnL by sign |
| Exposure time | Bars in position / total bars |
| Turnover | Total traded notional / average equity |

## Disclaimer

Backtests do not guarantee future performance. Results are hypothetical, exclude many real-world frictions, and are not financial advice.
