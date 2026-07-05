"use client";

import { useI18n } from "../lib/i18n";
import type { PaperRunState } from "../lib/types";
import { Badge, Card } from "./ui";

const STATUS_TONES: Record<string, "green" | "sky" | "slate" | "rose" | "amber"> = {
  running: "sky",
  completed: "green",
  stopped: "slate",
  failed: "rose",
  created: "amber",
};

export default function PaperRunStatusPanel({ run }: { run: PaperRunState }) {
  const { t } = useI18n();
  const statusKey = `paperRuns.status${run.status.charAt(0).toUpperCase()}${run.status.slice(1)}`;
  const pnl = run.current_equity - run.initial_capital;
  return (
    <Card
      title={`${run.symbol} · ${run.timeframe}`}
      actions={
        <div className="flex items-center gap-2">
          {run.is_mock_data && <Badge tone="amber">{t("common.mockData")}</Badge>}
          <Badge tone={STATUS_TONES[run.status] ?? "slate"}>{t(statusKey)}</Badge>
        </div>
      }
    >
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div>
          <div className="text-xs text-slate-500">{t("paperRuns.currentEquity")}</div>
          <div className="text-lg font-semibold text-slate-200">
            {run.current_equity.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-500">PnL</div>
          <div className={`text-lg font-semibold ${pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
            {pnl >= 0 ? "+" : ""}
            {pnl.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-500">{t("paperRuns.realizedPnl")}</div>
          <div className="text-lg font-semibold text-slate-200">{run.realized_pnl.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-xs text-slate-500">{t("paperRuns.unrealizedPnl")}</div>
          <div className="text-lg font-semibold text-slate-200">{run.unrealized_pnl.toFixed(2)}</div>
        </div>
      </div>
      {run.open_positions.length > 0 && (
        <div className="mt-3 border-t border-edge pt-3">
          <div className="mb-1 text-xs text-slate-500">{t("paperRuns.openPositions")}</div>
          {run.open_positions.map((pos) => (
            <div key={pos.symbol} className="flex items-center justify-between text-sm">
              <span>
                {pos.symbol} × {pos.quantity.toFixed(4)}
              </span>
              <span className="text-slate-400">
                {t("paperRuns.avgPrice")}: {pos.avg_price.toFixed(2)}
              </span>
              <span className={pos.unrealized_pnl >= 0 ? "text-emerald-400" : "text-rose-400"}>
                {pos.unrealized_pnl.toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
