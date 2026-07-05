# AlphaQuantPro — Product Spec

## Product

AlphaQuantPro is an AI quant trading / strategy agent workbench covering:
strategy code → deterministic backtest → paper/simulation run → run analysis → strategy review.

## Tenets

1. Strategy code is the source of truth.
2. Backtest results must be reproducible.
3. Simulation/paper trading is separated from live execution; live trading is disabled in MVP.
4. Every trade decision is logged.
5. AI assists, but the deterministic engine owns execution and metrics.
6. Deterministic calculations beat LLM guesses.
7. Paper/simulation first, real execution later (future work, gated).

## Target users

Quant developers, independent traders, AI strategy builders, and researchers who want reproducible strategy experiments with transparent logs and metrics.

## MVP user journey

1. Open the strategy workspace and create or edit a Python strategy (indicator or script style).
2. Configure symbol, timeframe, date range, capital, fees, slippage, and position sizing.
3. Run a deterministic backtest; inspect metrics, equity curve, drawdown, trades, and logs.
4. Start a paper/simulation run (historical replay or mock live feed); watch signals, orders, fills, and PnL update.
5. Stop the run and generate a post-run analysis (deterministic summary + DeepSeek commentary).
6. Request an AI strategy review or chat with the strategy assistant.

## Pages

`/dashboard`, `/strategies`, `/strategies/new`, `/strategies/[strategyId]`, `/backtests`, `/backtests/[backtestId]`, `/paper-runs`, `/paper-runs/[runId]`, `/market-data`, `/analysis`, `/settings`.

## Hard boundaries (MVP)

- No real broker execution, no billing, no multi-tenant auth, no mobile app, no social features.
- No hidden autonomous trading behavior.
- API keys live in backend environment variables only.
- Bilingual GUI: English and 简体中文, switchable at runtime.

## Definition of done

- App runs locally (docker compose or two dev servers).
- Strategy CRUD, backtest with metrics/chart/trades/logs, paper run start/stop, post-run analysis.
- GUI switches between English and 简体中文.
- LLM features use DeepSeek only; market data uses QVeris only (with labeled mock fallback).
- Live trading disabled.
