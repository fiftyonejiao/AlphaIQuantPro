"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import EquityCurveChart from "../../../components/EquityCurveChart";
import MetricCards from "../../../components/MetricCards";
import PaperRunStatusPanel from "../../../components/PaperRunStatusPanel";
import RunLogViewer from "../../../components/RunLogViewer";
import TradeTable from "../../../components/TradeTable";
import { Button, Card, ErrorNote, Spinner } from "../../../components/ui";
import { api } from "../../../lib/api";
import { useI18n } from "../../../lib/i18n";
import type { PaperRunState } from "../../../lib/types";

interface Analysis {
  deterministic_summary: string;
  ai_analysis: string;
  ai_is_mock: boolean;
  disclaimer: string;
}

export default function PaperRunDetailPage() {
  const { t, lang } = useI18n();
  const params = useParams<{ runId: string }>();
  const [run, setRun] = useState<PaperRunState | null | undefined>(undefined);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [stopping, setStopping] = useState(false);

  const load = useCallback(() => {
    api.get<PaperRunState>(`/api/paper-runs/${params.runId}`).then(setRun).catch(() => setRun(null));
  }, [params.runId]);

  useEffect(() => {
    load();
    const timer = setInterval(() => {
      setRun((current) => {
        if (current && current.status !== "running" && current.status !== "created") return current;
        load();
        return current;
      });
    }, 2000);
    return () => clearInterval(timer);
  }, [load]);

  const stop = async () => {
    setStopping(true);
    try {
      const state = await api.post<PaperRunState>(`/api/paper-runs/${params.runId}/stop`);
      setRun(state);
    } finally {
      setStopping(false);
    }
  };

  const generateAnalysis = async () => {
    setAnalyzing(true);
    try {
      const result = await api.get<Analysis>(`/api/paper-runs/${params.runId}/analysis?language=${lang}`);
      setAnalysis(result);
    } finally {
      setAnalyzing(false);
    }
  };

  if (run === undefined) return <Spinner label={t("common.loading")} />;
  if (run === null) return <ErrorNote message={t("common.error")} />;

  const active = run.status === "running" || run.status === "created";

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">
          {t("paperRuns.title")} · {run.run_id.slice(0, 12)}
        </h1>
        <div className="flex items-center gap-3">
          {active && (
            <Button variant="danger" onClick={stop} disabled={stopping}>
              {t("paperRuns.stopRun")}
            </Button>
          )}
          <Link href="/paper-runs" className="text-sm text-sky-400 hover:underline">
            {t("common.back")}
          </Link>
        </div>
      </div>

      <PaperRunStatusPanel run={run} />

      {Object.keys(run.metrics).length > 0 && <MetricCards metrics={run.metrics} />}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <EquityCurveChart data={run.equity_curve} />
          <TradeTable trades={run.trades} />
        </div>
        <div className="space-y-4">
          <Card title={t("paperRuns.signals")}>
            <div className="max-h-48 space-y-1 overflow-auto text-sm">
              {run.signals.length === 0 ? (
                <p className="text-slate-500">{t("common.empty")}</p>
              ) : (
                run.signals.map((s, i) => (
                  <div key={i} className="flex justify-between">
                    <span className="text-slate-400">{s.timestamp.slice(0, 10)}</span>
                    <span className={s.signal === 1 ? "text-emerald-400" : "text-slate-400"}>
                      {s.note} @ {s.price.toFixed(2)}
                    </span>
                  </div>
                ))
              )}
            </div>
          </Card>
          <RunLogViewer logs={run.logs} />
        </div>
      </div>

      {!active && (
        <Card
          title={t("paperRuns.postRunAnalysis")}
          actions={
            <Button onClick={generateAnalysis} disabled={analyzing}>
              {analyzing ? t("paperRuns.generatingAnalysis") : t("paperRuns.generateAnalysis")}
            </Button>
          }
        >
          {analysis ? (
            <div className="space-y-4 text-sm">
              <div>
                <h4 className="mb-1 font-semibold text-slate-300">{t("paperRuns.deterministicSummary")}</h4>
                <pre className="whitespace-pre-wrap rounded-lg bg-surface p-3 text-xs text-slate-400">
                  {analysis.deterministic_summary}
                </pre>
              </div>
              <div>
                <h4 className="mb-1 font-semibold text-slate-300">{t("paperRuns.aiAnalysis")}</h4>
                <p className="whitespace-pre-wrap text-slate-300">{analysis.ai_analysis}</p>
                {analysis.ai_is_mock && <p className="mt-2 text-xs text-amber-500">{t("analysis.mockNotice")}</p>}
              </div>
              <p className="text-xs text-slate-600">{analysis.disclaimer}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-500">{t("common.empty")}</p>
          )}
        </Card>
      )}
    </div>
  );
}
