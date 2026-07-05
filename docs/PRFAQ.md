# AlphaQuantPro — PR/FAQ

## Press Release

Today we are launching **AlphaQuantPro**, a self-hosted AI quant platform that connects strategy coding, deterministic backtesting, paper-style simulation, and run analysis in one workflow. Users can write Python strategies, test them historically, run them in a simulated environment, and review performance with clear metrics, logs, and risk analysis.

Unlike disconnected notebooks or black-box trading bots, this workbench makes every step visible: strategy code, parameters, backtest assumptions, execution logs, PnL, drawdown, trades, and AI-generated post-run analysis.

## FAQ

**Q: Can AlphaQuantPro trade real money?**
No. The MVP is simulation-only. Live trading is disabled, permanently gated in settings, and marked as future work. The `exchange_paper_future` mode is rejected by the API.

**Q: Where does market data come from?**
QVeris.ai is the only real data gateway (discover → inspect → call workflow). When the QVeris key is missing or a call fails, the system falls back to a deterministic, clearly labeled MOCK DATA generator so the whole workflow stays demoable and reproducible.

**Q: Which LLM does it use?**
DeepSeek only (`deepseek-chat` by default). There is no provider selector and no non-DeepSeek code path. Without a key, LLM features return clearly marked MOCK LLM OUTPUT while deterministic features keep working.

**Q: Does the AI compute my returns?**
Never. All metrics (returns, drawdown, Sharpe, win rate, profit factor, exposure, turnover) are computed by the deterministic engine. DeepSeek only reasons over engine outputs to produce commentary.

**Q: Are backtests reproducible?**
Yes. Same strategy code + same data + same config produces identical results. Mock data is seeded per symbol/timeframe.

**Q: Is this financial advice?**
No. Nothing in this project is financial advice. Backtests and simulations do not guarantee future performance. AI output may be wrong. All trading involves risk.
