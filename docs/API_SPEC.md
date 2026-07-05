# AlphaQuantPro — API Spec

Base URL: `http://localhost:8000`. Interactive docs at `/docs` (OpenAPI).

## Strategies

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/strategies` | Create a strategy (`name`, `description`, `strategy_type`, `code`, `parameters`) |
| GET | `/api/strategies` | List strategies |
| GET | `/api/strategies/{strategy_id}` | Get one strategy |
| PUT | `/api/strategies/{strategy_id}` | Update fields |
| DELETE | `/api/strategies/{strategy_id}` | Delete |

## Backtests

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/backtests` | Run a deterministic backtest (synchronous), persists the result |
| GET | `/api/backtests` | List backtest summaries |
| GET | `/api/backtests/{backtest_id}` | Full result (metrics, equity curve, trades, logs) |
| GET | `/api/backtests/{backtest_id}/events` | Run logs |
| GET | `/api/backtests/{backtest_id}/trades` | Trades |
| GET | `/api/backtests/{backtest_id}/metrics` | Metrics |

`POST /api/backtests` body: `strategy_id`, `symbol`, `timeframe` (`1d|1h|15m`), `start_date`, `end_date`, `initial_capital`, `fee_rate`, `slippage`, `position_size` (0-1], `parameters`, `random_seed`.

Errors: `404` unknown strategy; `422` malformed market data, invalid config, or strategy sandbox error.

## Paper runs (simulation only)

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/paper-runs` | Start a run (`mode`: `historical_replay` or `mock_live`; `exchange_paper_future` is rejected — future work) |
| GET | `/api/paper-runs` | List runs (live + persisted) |
| GET | `/api/paper-runs/{run_id}` | Live state: equity, positions, signals, orders, fills, logs |
| POST | `/api/paper-runs/{run_id}/stop` | Stop the run |
| GET | `/api/paper-runs/{run_id}/events` | Logs + signals |
| GET | `/api/paper-runs/{run_id}/trades` | Trades, orders, fills |
| GET | `/api/paper-runs/{run_id}/analysis?language=en\|zh-CN` | Post-run analysis (run must not be running) |

## Market data (QVeris gateway)

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/market-data/sources` | Available capabilities (QVeris or labeled mock) |
| GET | `/api/market-data/status` | Gateway status and active source |
| POST | `/api/market-data/fetch` | Fetch normalized OHLCV (`symbol`, `timeframe`, `start_date`, `end_date`) |
| GET | `/api/market-data/qveris/status` | QVeris configuration/reachability (never returns the key) |
| POST | `/api/market-data/qveris/fetch` | Fetch via the QVeris path |
| GET | `/api/market-data/qveris/sources` | QVeris discover results |

## Analysis (DeepSeek only)

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/analysis/strategy-review` | AI strategy review (`strategy_id`, optional `backtest_id`, `language`) |
| POST | `/api/analysis/assistant-chat` | AI assistant chat (`message`, optional `strategy_id`, `history`, `language`) |

Without `DEEPSEEK_API_KEY`, responses are clearly marked mock output (`is_mock: true`).

## Settings

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/settings` | Workbench defaults + DeepSeek/QVeris status (no keys ever) |
| PUT | `/api/settings` | Update defaults; `live_trading_enabled` cannot be set to true |
