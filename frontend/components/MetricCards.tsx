"use client";

import { useI18n } from "../lib/i18n";
import type { Metrics } from "../lib/types";

function fmtPct(v: number | null | undefined, na: string): string {
  if (v === null || v === undefined) return na;
  return `${(v * 100).toFixed(2)}%`;
}

function fmtNum(v: number | null | undefined, na: string, digits = 2): string {
  if (v === null || v === undefined) return na;
  return v.toFixed(digits);
}

export default function MetricCards({ metrics }: { metrics: Partial<Metrics> }) {
  const { t } = useI18n();
  const na = t("metrics.notAvailable");
  const items: { label: string; value: string; tone?: "pos" | "neg" }[] = [
    {
      label: t("metrics.totalReturn"),
      value: fmtPct(metrics.total_return, na),
      tone: (metrics.total_return ?? 0) >= 0 ? "pos" : "neg",
    },
    { label: t("metrics.cagr"), value: fmtPct(metrics.cagr, na) },
    { label: t("metrics.maxDrawdown"), value: fmtPct(metrics.max_drawdown, na), tone: "neg" },
    { label: t("metrics.sharpe"), value: fmtNum(metrics.sharpe, na) },
    { label: t("metrics.winRate"), value: fmtPct(metrics.win_rate, na) },
    { label: t("metrics.profitFactor"), value: fmtNum(metrics.profit_factor, na) },
    { label: t("metrics.tradeCount"), value: String(metrics.trade_count ?? 0) },
    { label: t("metrics.exposureTime"), value: fmtPct(metrics.exposure_time, na) },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="rounded-xl border border-edge bg-panel p-3">
          <div className="text-xs text-slate-500">{item.label}</div>
          <div
            className={`mt-1 text-lg font-semibold ${
              item.tone === "pos" ? "text-emerald-400" : item.tone === "neg" ? "text-rose-400" : "text-slate-200"
            }`}
          >
            {item.value}
          </div>
        </div>
      ))}
    </div>
  );
}
