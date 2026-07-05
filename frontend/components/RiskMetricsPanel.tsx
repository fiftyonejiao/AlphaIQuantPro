"use client";

import { useI18n } from "../lib/i18n";
import type { Metrics } from "../lib/types";
import { Card } from "./ui";

export default function RiskMetricsPanel({ metrics }: { metrics: Partial<Metrics> }) {
  const { t } = useI18n();
  const na = t("metrics.notAvailable");
  const rows = [
    { label: t("metrics.maxDrawdown"), value: metrics.max_drawdown != null ? `${(metrics.max_drawdown * 100).toFixed(2)}%` : na },
    { label: t("metrics.sharpe"), value: metrics.sharpe != null ? metrics.sharpe.toFixed(2) : na },
    { label: t("metrics.avgWin"), value: metrics.avg_win != null ? metrics.avg_win.toFixed(2) : na },
    { label: t("metrics.avgLoss"), value: metrics.avg_loss != null ? metrics.avg_loss.toFixed(2) : na },
    { label: t("metrics.exposureTime"), value: metrics.exposure_time != null ? `${(metrics.exposure_time * 100).toFixed(1)}%` : na },
    { label: t("metrics.turnover"), value: metrics.turnover != null ? metrics.turnover.toFixed(2) : na },
  ];
  return (
    <Card title={t("backtests.drawdown") + " / " + t("metrics.sharpe")}>
      <dl className="space-y-2">
        {rows.map((row) => (
          <div key={row.label} className="flex items-center justify-between text-sm">
            <dt className="text-slate-500">{row.label}</dt>
            <dd className="font-medium text-slate-200">{row.value}</dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}
