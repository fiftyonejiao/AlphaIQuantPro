"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import DrawdownChart from "../../../components/DrawdownChart";
import EquityCurveChart from "../../../components/EquityCurveChart";
import MetricCards from "../../../components/MetricCards";
import RiskMetricsPanel from "../../../components/RiskMetricsPanel";
import RunLogViewer from "../../../components/RunLogViewer";
import TradeTable from "../../../components/TradeTable";
import { Badge, ErrorNote, Spinner } from "../../../components/ui";
import { api } from "../../../lib/api";
import { useI18n } from "../../../lib/i18n";
import type { BacktestResult } from "../../../lib/types";

export default function BacktestDetailPage() {
  const { t } = useI18n();
  const params = useParams<{ backtestId: string }>();
  const [result, setResult] = useState<BacktestResult | null | undefined>(undefined);

  useEffect(() => {
    api
      .get<BacktestResult>(`/api/backtests/${params.backtestId}`)
      .then(setResult)
      .catch(() => setResult(null));
  }, [params.backtestId]);

  if (result === undefined) return <Spinner label={t("common.loading")} />;
  if (result === null) return <ErrorNote message={t("common.error")} />;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold">
            {result.symbol} · {result.timeframe}
          </h1>
          <Badge tone="slate">
            {result.start_date} → {result.end_date}
          </Badge>
          {result.is_mock_data && <Badge tone="amber">{t("common.mockData")}</Badge>}
        </div>
        <Link href="/backtests" className="text-sm text-sky-400 hover:underline">
          {t("common.back")}
        </Link>
      </div>

      <MetricCards metrics={result.metrics} />

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <EquityCurveChart data={result.equity_curve} />
          <DrawdownChart data={result.equity_curve} />
        </div>
        <div className="space-y-4">
          <RiskMetricsPanel metrics={result.metrics} />
          <RunLogViewer logs={result.logs} />
        </div>
      </div>

      <TradeTable trades={result.trades} />
    </div>
  );
}
