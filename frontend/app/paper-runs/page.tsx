"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Badge, Button, Card, EmptyState, ErrorNote, Field, inputClass, Spinner } from "../../components/ui";
import { api } from "../../lib/api";
import { useI18n } from "../../lib/i18n";
import type { PaperRunState, Strategy } from "../../lib/types";

const STATUS_TONES: Record<string, "green" | "sky" | "slate" | "rose" | "amber"> = {
  running: "sky",
  completed: "green",
  stopped: "slate",
  failed: "rose",
  created: "amber",
};

export default function PaperRunsPage() {
  const { t } = useI18n();
  const [runs, setRuns] = useState<PaperRunState[] | null>(null);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [strategyId, setStrategyId] = useState("");
  const [symbol, setSymbol] = useState("AAPL");
  const [mode, setMode] = useState("historical_replay");
  const [lookbackDays, setLookbackDays] = useState(120);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");

  const load = () => api.get<PaperRunState[]>("/api/paper-runs").then(setRuns).catch(() => setRuns([]));

  useEffect(() => {
    load();
    api.get<Strategy[]>("/api/strategies").then((list) => {
      setStrategies(list);
      if (list.length > 0) setStrategyId(list[0].strategy_id);
    });
    const timer = setInterval(load, 3000);
    return () => clearInterval(timer);
  }, []);

  const start = async () => {
    setError("");
    setStarting(true);
    try {
      await api.post("/api/paper-runs", {
        strategy_id: strategyId,
        symbol,
        mode,
        lookback_days: lookbackDays,
        replay_delay_seconds: 0.2,
      });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setStarting(false);
    }
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold">{t("paperRuns.title")}</h1>
        <p className="text-sm text-amber-500">{t("paperRuns.subtitle")}</p>
      </div>

      <Card title={t("paperRuns.start")}>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
          <Field label={t("backtests.strategy")}>
            <select className={inputClass} value={strategyId} onChange={(e) => setStrategyId(e.target.value)}>
              {strategies.map((s) => (
                <option key={s.strategy_id} value={s.strategy_id}>
                  {s.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label={t("common.symbol")}>
            <input className={inputClass} value={symbol} onChange={(e) => setSymbol(e.target.value)} />
          </Field>
          <Field label={t("paperRuns.mode")}>
            <select className={inputClass} value={mode} onChange={(e) => setMode(e.target.value)}>
              <option value="historical_replay">{t("paperRuns.modeReplay")}</option>
              <option value="mock_live">{t("paperRuns.modeMockLive")}</option>
            </select>
          </Field>
          <Field label={t("paperRuns.lookbackDays")}>
            <input type="number" className={inputClass} value={lookbackDays} onChange={(e) => setLookbackDays(Number(e.target.value))} />
          </Field>
          <div className="flex items-end">
            <Button onClick={start} disabled={starting || !strategyId} className="w-full">
              {starting ? t("paperRuns.starting") : t("paperRuns.start")}
            </Button>
          </div>
        </div>
        {error && <div className="mt-3"><ErrorNote message={error} /></div>}
      </Card>

      {runs === null ? (
        <Spinner label={t("common.loading")} />
      ) : runs.length === 0 ? (
        <EmptyState label={t("common.empty")} />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {runs.map((run) => {
            const statusKey = `paperRuns.status${run.status.charAt(0).toUpperCase()}${run.status.slice(1)}`;
            const pnl = run.current_equity - run.initial_capital;
            return (
              <Link key={run.run_id} href={`/paper-runs/${run.run_id}`}>
                <Card className="transition hover:border-sky-800">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">
                      {run.symbol} · {run.timeframe}
                    </span>
                    <div className="flex gap-2">
                      {run.is_mock_data && <Badge tone="amber">{t("common.mockData")}</Badge>}
                      <Badge tone={STATUS_TONES[run.status] ?? "slate"}>{t(statusKey)}</Badge>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center justify-between text-sm">
                    <span className="text-slate-500">{t("paperRuns.currentEquity")}</span>
                    <span className="font-medium">
                      {run.current_equity.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      <span className={`ml-2 ${pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                        ({pnl >= 0 ? "+" : ""}
                        {pnl.toLocaleString(undefined, { maximumFractionDigits: 0 })})
                      </span>
                    </span>
                  </div>
                  <div className="mt-1 text-xs text-slate-600">{run.run_id.slice(0, 12)}</div>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
