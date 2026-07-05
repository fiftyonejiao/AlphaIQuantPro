# AlphaQuantPro — Complete Project Prompt

> **This README is a complete, self-contained project prompt.** Paste it into your coding agent (Cursor, Codex, etc.) to generate **AlphaQuantPro** — a local-first, auditable AI quant trading / strategy agent workbench. It follows Amazon Working-Backwards spec discipline: customer problem first, tenets, explicit goals and non-goals, phased implementation, and a hard definition of done.

---

## 0. Role And Operating Mode

You are a principal product architect, senior full-stack engineer, quant platform engineer, trading-system designer, and AI agent systems builder. Your job is to generate a production-quality, local-first MVP for **AlphaQuantPro**, an AI quant trading / strategy agent workbench inspired by https://github.com/brokermr810/QuantDinger.

You are not a generic code generator. You operate as a builder with this combined background:

- A developer with practical experience building AI Agents, LLM applications, tool-calling systems, multi-agent orchestration, agent memory, structured outputs, and agent evaluation loops.
- An investment and trading enthusiast with real accumulated understanding of public markets, quantitative trading, asset allocation, portfolio construction, drawdown control, risk management, and strategy evaluation.
- A product manager / startup builder who can turn investment and trading ideas into usable product prototypes, not just code.
- A technical team member comfortable with data engineering, market data pipelines, strategy backtesting, financial modeling, trading-system architecture, execution simulation, logs, and performance analytics.
- A researcher and builder exploring AI-assisted quantitative trading in a disciplined, auditable, user-friendly way.

中文背景（保留产品意图）：

- 对 AI Agent、LLM 应用、工具调用、多 Agent 协作有实践经验的开发者。
- 对二级市场、量化交易、资产配置、风险管理有真实积累的投资交易爱好者。
- 能把投资想法转化为产品原型的产品经理或创业者。
- 熟悉数据工程、策略回测、金融建模、交易系统的技术团队。
- 希望探索 AI 投资交易的研究者和 builders。

This background must influence architecture decisions:

- Build agent workflows as inspectable systems, not mystical chatbots.
- Treat financial numbers and trading metrics as deterministic calculations with assumptions, sources, timestamps, and validation — never free-form LLM guesses.
- Keep quant execution infrastructure separate from qualitative investment memo generation.
- Keep every AI output explainable, reviewable, logged, and exportable.
- Prefer productized workflows over raw prompt demos.
- Prefer simulation, paper trading, and audit logs before any real-money execution.
- Design for a serious builder who wants to ship a working prototype, not a decorative demo.

Act like an Amazon-style Working Backwards product team:

- Start from the customer problem.
- Define the product promise clearly.
- Separate tenets, goals, non-goals, requirements, metrics, and launch criteria.
- Make one-way-door decisions explicit; keep two-way-door decisions reversible.
- Avoid scope creep. Prefer a small working system over a huge broken system.
- Build in phases with acceptance criteria.

## 1. Product Summary

**AlphaQuantPro** is an AI quant trading / strategy agent workbench.

The product delivers one complete, connected quant workflow:

1. Strategy code
2. Deterministic backtest
3. Paper/simulation run
4. Live-like run analysis
5. Strategy performance review

**Hard rule:** AlphaQuantPro must not enable real-money trading in the MVP. If any live trading placeholder exists, it must be clearly disabled and marked as future work.

## 2. Reference Repository

Inspect this reference repository before coding, as the main conceptual source:

- https://github.com/brokermr810/QuantDinger

Rules:

- Regenerate a clean, understandable AI quant workbench with strategy development, backtest, paper/simulation run, and run analysis.
- Do not blindly clone every feature.
- Keep the MVP local-first, deterministic, auditable, and demoable.

### 2.1 Attribution And Naming Guardrail

- The generated AlphaQuantPro codebase must **not** include the original reference project name in source code, package names, module names, class names, function names, variables, database table names, API paths, route names, UI labels, README branding, comments, tests, Docker files, environment variable prefixes, or generated documentation.
- The original name may appear only in this prompt specification and in an optional private engineering note named `REFERENCE_SOURCES.md`, if generated.
- Do not create files, folders, commands, npm packages, Python packages, or UI pages named after the reference project or its author.
- Do not write phrases such as "powered by …", "… clone", or "regenerated …" referencing the original project in any user-facing screen or public documentation.
- Translate all borrowed concepts into AlphaQuantPro-native names such as `strategy_lab`, `backtest_engine`, `simulation_runner`, `run_analyzer`, `trade_ledger`, and `performance_report`.
- The product identity must remain **AlphaQuantPro**. The reference repository is an inspiration source, not a runtime dependency or brand name.

## 3. Required Financial Stock Data Provider: QVeris.ai

All financial stock-data analysis, market-data access, historical bars, quote retrieval, and data-provider discovery must use **QVeris.ai** as the primary data access layer. Treat QVeris as the unified capability-routing and financial-data gateway for AlphaQuantPro.

Implementation rules:

- Use QVeris.ai before adding any direct market-data provider integration.
- Implement a dedicated `QverisClient` wrapper and keep all QVeris calls behind `market_data_service.py`.
- Use the QVeris **discover → inspect → call** workflow when selecting stock quote, OHLCV, historical bars, corporate action, news, or indicator source-data capabilities.
- Normalize all QVeris responses into deterministic internal market-data schemas before the backtest engine or paper/simulation engine can consume them.
- Store every retrieved data point with provider name, QVeris tool/capability id when available, source timestamp, retrieval timestamp, symbol, market, timeframe, currency, and data-quality notes.
- Never let the LLM invent price bars, quotes, fills, corporate actions, volumes, spreads, slippage, financial statements, or trading metrics.
- If QVeris is unavailable or the API key is missing, fall back only to explicit mock/demo data and clearly show `MOCK DATA` in the UI, backtest result, and run logs.

Required environment variables:

```bash
QVERIS_API_KEY="${QVERIS_API_KEY}"
QVERIS_BASE_URL="https://qveris.ai/api/v1"
QVERIS_SESSION_ID="alphaquantpro-local"
```

Secret-handling rules:

- The real QVeris API key lives in local `.env` / `.env.local` only.
- `.env.example` must contain only `QVERIS_API_KEY=your_qveris_api_key_here`.
- Never hardcode the raw API key in source code, committed documentation, frontend bundles, logs, screenshots, generated reports, test snapshots, or seed data.
- Backend reads the key from environment variables. The frontend must never receive or display the QVeris API key.

Required data categories through QVeris:

- Historical OHLCV bars for backtesting.
- Latest quotes for market-data status and simulation context.
- Corporate actions if available: splits, dividends, symbol changes.
- Trading calendar/session data if available.
- News/sentiment as optional strategy-context data, never as deterministic price data.
- Provider metadata, latency, coverage, and rate-limit status when available.

Required backend modules:

```text
backend/app/services/qveris_client.py
backend/app/services/market_data_service.py
backend/app/services/data_normalization_service.py
backend/app/schemas/qveris.py
```

Required validation behavior:

- Backtests must refuse to run if required OHLCV fields are missing or malformed.
- Paper/simulation runs must log the market-data source and whether data is live-like, delayed, historical replay, or mock.
- Add tests for QVeris client initialization, missing API key behavior, mock fallback, OHLCV normalization, and malformed data rejection.

## 4. Required DeepSeek-Only LLM Runtime

All LLM-powered features must use **DeepSeek only**. Do not generate OpenAI, Anthropic/Claude, Gemini, Grok, Mistral, Cohere, local Ollama, or multi-provider fallback code unless this specification is explicitly changed later.

Implementation rules:

- Implement a backend-only `DeepSeekClient` wrapper instead of scattering raw model calls across services.
- Keep all LLM prompts, tool-call orchestration, memo generation, strategy review, and agent commentary behind DeepSeek service modules.
- Never expose the DeepSeek API key to the frontend, logs, screenshots, generated reports, tests, browser storage, or client-side bundles.
- Do not create a model-provider selector in the GUI. Settings may show only DeepSeek connection status, selected DeepSeek model name, and cost/usage telemetry if available.
- Generated code must not contain non-DeepSeek provider imports, SDK clients, environment variables, adapters, route names, comments, examples, or documentation.
- QVeris.ai remains the source of financial data. DeepSeek may reason over normalized QVeris data, but DeepSeek must never invent market data, financial statements, prices, indicators, fills, valuation inputs, or metrics.
- If the DeepSeek API key is missing, LLM features must be disabled or use explicit mock/demo text clearly marked as `MOCK LLM OUTPUT`; deterministic calculations and QVeris data access must still work when possible.

Required environment variables:

```bash
DEEPSEEK_API_KEY="your_deepseek_api_key_here"
DEEPSEEK_BASE_URL="https://api.deepseek.com"
DEEPSEEK_MODEL="deepseek-chat"
```

Model rules:

- Default model is `deepseek-chat` unless the builder intentionally configures another official DeepSeek model through `DEEPSEEK_MODEL`.
- Any configured model must remain inside the DeepSeek model family.
- Never silently fall back to any non-DeepSeek model.

Required backend modules:

```text
backend/app/services/deepseek_client.py
backend/app/services/llm_service.py
backend/app/schemas/llm.py
```

Required validation behavior:

- Add tests proving that no non-DeepSeek provider environment variables are required.
- Add tests for missing `DEEPSEEK_API_KEY` behavior.
- Add tests proving report/memo/analysis generation uses the DeepSeek service boundary.

## 5. Required Bilingual GUI: English And 简体中文

Every graphical user interface must support switching between **English** and **简体中文**. The language switch must be visible, persistent, and applied consistently across pages, forms, tables, charts, empty states, error messages, confirmations, settings, reports, and exported UI-rendered text.

Implementation rules:

- Support exactly two language codes for MVP: `en` and `zh-CN`.
- Add a `LanguageSwitcher` component in the top navigation or settings area.
- Persist the selected language in local storage and/or user settings.
- Detect browser language only as an initial default; the user's manual choice always overrides browser detection.
- No hardcoded user-facing UI strings in components — use translation keys.
- All validation errors, loading states, empty states, chart labels, table headers, buttons, menus, tooltips, and report-rendering labels must use the i18n layer.
- LLM-generated memos, analysis explanations, and strategy-review text should follow the selected UI language unless the user explicitly chooses another report language.
- Use **简体中文**, not 繁體中文, for the Chinese interface.

Required frontend modules:

```text
frontend/lib/i18n.ts
frontend/locales/en.json
frontend/locales/zh-CN.json
frontend/components/LanguageSwitcher.tsx
```

Acceptance criteria:

- User can switch the full GUI from English to 简体中文 without restarting the app.
- User can switch back from 简体中文 to English without losing current page state.
- New pages/components fail review if they introduce hardcoded user-facing strings outside the translation system.

## 6. Product Boundary

AlphaQuantPro **is for**:

- Quant developers.
- Strategy researchers.
- AI-assisted strategy builders.
- Users who need code → backtest → simulation/paper run → analysis.
- Users who want a structured AI quant trading workbench.

AlphaQuantPro **is not for**:

- Value investing memo generation as the primary product.
- Warren Buffett-style qualitative investing as the main UX.
- Uncontrolled real-money trading by default.
- Black-box AI trading without deterministic logs.
- Broker automation in the MVP.

## 7. Amazon-Style Press Release

Today we are launching **AlphaQuantPro**, a self-hosted AI quant platform that connects strategy coding, deterministic backtesting, paper-style simulation, and run analysis in one workflow. Users can write or generate Python strategies, test them historically, run them in a simulated environment, and review performance with clear metrics, logs, and risk analysis.

Unlike disconnected notebooks or black-box trading bots, this workbench makes every step visible: strategy code, parameters, backtest assumptions, execution logs, PnL, drawdown, trades, and AI-generated post-run analysis.

## 8. Product Tenets

1. Strategy code is the source of truth.
2. Backtest results must be reproducible.
3. Simulation/paper trading must be separated from live execution.
4. Live trading, if implemented later, must be gated and disabled by default.
5. Every trade decision must be logged.
6. AI can assist, but the deterministic engine owns execution and metrics.
7. Visible workflow beats hidden AI magic.
8. Structured output beats long unstructured chat.
9. Human control beats autonomous overreach.
10. Deterministic calculations beat LLM guesses.
11. Logs and evidence beat unsupported claims.
12. Paper/simulation first, real execution later.
13. Small working MVP beats large broken platform.

## 9. Customer Problem

Quant users jump between notebooks, scripts, charting tools, backtest libraries, and exchange dashboards. This causes fragmented workflow, unreproducible backtests, unclear strategy changes, and poor paper/live run review. Users need one structured workbench that connects strategy code, backtesting, simulation/paper running, and performance analysis.

## 10. Target User

- Quant developer.
- Independent trader.
- AI strategy builder.
- Crypto/stocks/forex researcher.
- Developer who wants self-hosted strategy infrastructure.
- Data engineer or financial-modeling builder who wants reproducible strategy experiments.
- Researcher exploring AI-assisted quantitative trading with transparent logs, metrics, and deterministic run records.

## 11. MVP User Journey

1. User opens the strategy workspace.
2. User creates or imports a Python strategy.
3. User selects market, symbol, timeframe, and date range.
4. User runs a deterministic backtest.
5. UI displays performance metrics, equity curve, trades, logs, and drawdown.
6. User sends the strategy into paper/simulation mode.
7. System records simulated trade decisions.
8. User reviews run analysis and AI-generated improvement suggestions.

## 12. Required UI Pages

- `/dashboard`
- `/strategies`
- `/strategies/new`
- `/strategies/[strategyId]`
- `/backtests`
- `/backtests/[backtestId]`
- `/paper-runs`
- `/paper-runs/[runId]`
- `/market-data`
- `/analysis`
- `/settings`

Do not include real-money trading as P0. Any live trading placeholder must be clearly disabled and marked as future work.

## 13. Required UI Components

- `StrategyEditor`
- `StrategyParameterPanel`
- `BacktestConfigForm`
- `BacktestRunButton`
- `EquityCurveChart`
- `DrawdownChart`
- `TradeTable`
- `MetricCards`
- `RunLogViewer`
- `PaperRunStatusPanel`
- `StrategyAIAssistantPanel`
- `RiskMetricsPanel`
- `BacktestComparisonTable`
- `MarketDataStatusCard`
- `DeepSeekStatusBadge`
- `LanguageSwitcher`

## 14. Navigation

- Dashboard
- Strategies
- Backtests
- Paper Runs
- Market Data
- Analysis
- Settings

## 15. Backend Services

```text
backend/
  app/
    main.py
    api/
      strategies.py
      backtests.py
      paper_runs.py
      market_data.py
      analysis.py
      settings.py
    services/
      strategy_service.py
      strategy_sandbox.py
      backtest_engine.py
      paper_trading_engine.py
      qveris_client.py
      deepseek_client.py
      llm_service.py
      market_data_service.py
      data_normalization_service.py
      metrics_service.py
      run_analysis_service.py
      ai_strategy_assistant.py
    schemas/
      strategy.py
      backtest.py
      paper_run.py
      trade.py
      metrics.py
      market_data.py
      qveris.py
      llm.py
    storage/
      database.py
      models.py
```

## 16. API Endpoints

```text
POST   /api/strategies
GET    /api/strategies
GET    /api/strategies/{strategy_id}
PUT    /api/strategies/{strategy_id}
DELETE /api/strategies/{strategy_id}

POST   /api/backtests
GET    /api/backtests
GET    /api/backtests/{backtest_id}
GET    /api/backtests/{backtest_id}/events
GET    /api/backtests/{backtest_id}/trades
GET    /api/backtests/{backtest_id}/metrics

POST   /api/paper-runs
GET    /api/paper-runs
GET    /api/paper-runs/{run_id}
POST   /api/paper-runs/{run_id}/stop
GET    /api/paper-runs/{run_id}/events
GET    /api/paper-runs/{run_id}/trades
GET    /api/paper-runs/{run_id}/analysis

GET    /api/market-data/sources
GET    /api/market-data/status
POST   /api/market-data/fetch
GET    /api/market-data/qveris/status
POST   /api/market-data/qveris/fetch
GET    /api/market-data/qveris/sources

POST   /api/analysis/strategy-review
GET    /api/settings
PUT    /api/settings
```

## 17. Strategy Types

Support at least two strategy styles:

1. **Indicator Strategy**
   - DataFrame-based; easier for users.
   - Examples: moving average crossover, RSI, Bollinger Band.

2. **Script Strategy**
   - Event-driven; more flexible.
   - Hooks: `on_bar`, `on_tick`, `on_signal`, `on_order_update`.

## 18. Backtest Workflow

The backtest engine must support:

- Symbol, timeframe, start date, end date
- Initial capital, fee rate, slippage, position sizing
- Strategy parameters
- Deterministic random seed if needed
- Trade logs
- Metrics calculation

Required metrics:

- Total return
- CAGR (if date range supports it)
- Max drawdown
- Sharpe ratio (if enough data exists)
- Win rate
- Profit factor
- Number of trades
- Average win / average loss
- Exposure time
- Turnover

## 19. Paper/Simulation Workflow

The paper trading engine must support:

- Start a paper run from a strategy.
- Use historical replay or a mocked live market feed for MVP.
- Record every signal, simulated order, and simulated fill.
- Record unrealized and realized PnL.
- Allow the user to stop a run.
- Generate run analysis after stopping.

## 20. Output Schemas

Backtest result schema:

```json
{
  "backtest_id": "string",
  "strategy_id": "string",
  "symbol": "string",
  "timeframe": "string",
  "start_date": "string",
  "end_date": "string",
  "initial_capital": 100000,
  "final_equity": 0,
  "metrics": {
    "total_return": 0,
    "max_drawdown": 0,
    "sharpe": 0,
    "win_rate": 0,
    "profit_factor": 0,
    "trade_count": 0
  },
  "equity_curve": [
    {
      "timestamp": "string",
      "equity": 0
    }
  ],
  "trades": [
    {
      "timestamp": "string",
      "symbol": "string",
      "side": "buy | sell",
      "quantity": 0,
      "price": 0,
      "fee": 0,
      "reason": "string"
    }
  ],
  "logs": ["string"]
}
```

Paper run schema:

```json
{
  "run_id": "string",
  "strategy_id": "string",
  "status": "created | running | stopped | failed | completed",
  "mode": "historical_replay | mock_live | exchange_paper_future",
  "started_at": "string",
  "stopped_at": "string",
  "current_equity": 0,
  "open_positions": [],
  "signals": [],
  "orders": [],
  "fills": [],
  "metrics": {},
  "post_run_analysis": "string"
}
```

## 21. Recommended Tech Stack

- **Frontend:** Next.js + TypeScript + Tailwind + shadcn/ui
- **Backend:** FastAPI + Python
- **Financial/market data:** QVeris.ai via backend-only `QverisClient`
- **Database:** SQLite for MVP, PostgreSQL-ready abstraction
- **Backtest engine:** custom minimal deterministic engine first
- **Charts:** lightweight charting or ECharts
- **Strategy sandbox:** restricted local execution with warnings
- **Streaming:** Server-Sent Events first
- **LLM provider:** DeepSeek only, for optional AI assistant features; deterministic backtests and paper/simulation runs must not depend on LLM output

Do not overbuild infrastructure. Local-first Docker Compose is enough for MVP.

## 22. Repository Structure

```text
AlphaQuantPro/
  README.md
  docker-compose.yml
  .env.example
  frontend/
    lib/i18n.ts
    locales/en.json
    locales/zh-CN.json
  backend/
  docs/
    PRFAQ.md
    PRODUCT_SPEC.md
    API_SPEC.md
    STRATEGY_SPEC.md
    BACKTEST_SPEC.md
  examples/
    strategies/
      moving_average_crossover.py
      rsi_reversion.py
    sample_backtest_result.json
```

## 23. Implementation Order

1. Create project skeleton.
2. Build strategy CRUD.
3. Build simple strategy editor UI.
4. Implement QVeris client, OHLCV normalization, and mock fallback.
5. Build minimal backtest engine.
6. Add sample strategies.
7. Add backtest result UI.
8. Add paper/simulation run engine.
9. Add paper run UI.
10. Add post-run analysis.
11. Add docs and examples.

## 24. Coding Agent Execution Rules

1. First inspect the reference repository and summarize what will be reused conceptually.
2. Do not copy large blocks blindly.
3. Generate only this project.
4. Keep every feature behind a clear acceptance criterion.
5. Prefer mock data first, then real implementation.
6. Use QVeris.ai for financial stock data and market-data analysis, with backend-only API-key access.
7. Use DeepSeek as the only LLM runtime; do not generate any non-DeepSeek provider code.
8. Implement full GUI language switching between English and 简体中文.
9. Keep UI clean and builder-friendly.
10. Add type definitions before wiring complex UI.
11. Add tests for backend services.
12. Add examples so the project can be demoed quickly.
13. Do not add real trading execution in MVP.
14. Do not create hidden autonomous trading behavior.
15. Do not use AI output as deterministic calculation.
16. Keep all financial disclaimers visible in docs and UI.
17. Run lint/test/build before final answer.
18. Report exactly what was created and what remains incomplete.

## 25. Financial Safety And Disclaimer Requirements

The project must include:

- Clear disclaimer: not financial advice.
- Paper/simulation-first language.
- Warning that AI output may be wrong.
- Warning that backtests do not guarantee future performance.
- No default real-money execution.
- No hidden broker/API-key behavior.
- No promise of profitability.
- Trading risk warning.
- Strategy execution log requirement.
- User confirmation gates for any future live trading.
- Environment variable isolation for API keys.

## 26. Definition Of Done

AlphaQuantPro is done when:

- [ ] App can run locally.
- [ ] User can create/edit a strategy.
- [ ] User can run a backtest.
- [ ] User can inspect metrics, chart, trades, and logs.
- [ ] User can start and stop a paper/simulation run.
- [ ] User can view post-run analysis.
- [ ] README explains setup and usage.
- [ ] GUI can switch between English and 简体中文.
- [ ] LLM features use DeepSeek only.
- [ ] Live trading is disabled or future-only.

## 27. First Prompt To Execute In Cursor/Codex

Use this exact instruction first:

```text
Generate a standalone repository named AlphaQuantPro using Amazon Working-Backwards product spec discipline.

AlphaQuantPro should be regenerated from the reference concept into a clean AI quant workbench covering strategy code, deterministic backtest, paper/simulation run, and run analysis. It must not enable real-money trading in MVP.

First inspect the reference repository. Then produce a short architecture plan. After that, implement AlphaQuantPro as a runnable MVP. Keep scope minimal, structured, auditable, builder-friendly, and demoable. Use QVeris.ai for all financial/market data, use DeepSeek as the only LLM runtime, and make the full GUI switchable between English and 简体中文.
```

## 28. Do Not Build These In MVP

- Real broker execution.
- Payment/billing system.
- Multi-tenant SaaS auth.
- Mobile app.
- Social sharing.
- Complex vector memory.
- Warren Buffett-style qualitative investing product as the main UX.
- A full clone of the reference project with every feature.
- Crypto exchange live execution.
- Production security claims.

## 29. Final Expected Output From Coding Agent

At the end, provide:

1. Summary of created files.
2. Local run instructions.
3. Features implemented.
4. Features intentionally skipped.
5. Known limitations.
6. Next recommended phase.
7. Test/build results.

---

> **Disclaimer:** AlphaQuantPro is a research and prototyping workbench. Nothing in this project is financial advice. Backtest results do not guarantee future performance. AI output may be wrong. All trading involves risk. The MVP performs paper/simulation only — no real-money execution.
