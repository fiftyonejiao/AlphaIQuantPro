"use client";

import Link from "next/link";
import { useI18n } from "../lib/i18n";
import type { BacktestSummary } from "../lib/types";
import { Badge, Card, EmptyState } from "./ui";

export default function BacktestComparisonTable({ backtests }: { backtests: BacktestSummary[] }) {
  const { t } = useI18n();
  return (
    <Card title={t("backtests.comparison")}>
      {backtests.length === 0 ? (
        <EmptyState label={t("common.empty")} />
      ) : (
        <div className="overflow-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs text-slate-500">
              <tr>
                <th className="pb-2 pr-3">{t("backtests.strategy")}</th>
                <th className="pb-2 pr-3">{t("common.symbol")}</th>
                <th className="pb-2 pr-3">{t("backtests.return")}</th>
                <th className="pb-2 pr-3">{t("backtests.maxDrawdown")}</th>
                <th className="pb-2 pr-3">{t("backtests.tradeCount")}</th>
                <th className="pb-2 pr-3">{t("common.status")}</th>
                <th className="pb-2">{t("common.actions")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-edge">
              {backtests.map((bt) => (
                <tr key={bt.backtest_id}>
                  <td className="py-2 pr-3">{bt.strategy_name || bt.strategy_id.slice(0, 8)}</td>
                  <td className="py-2 pr-3">
                    {bt.symbol}
                    {bt.is_mock_data && (
                      <span className="ml-1.5">
                        <Badge tone="amber">{t("common.mockData")}</Badge>
                      </span>
                    )}
                  </td>
                  <td className={`py-2 pr-3 font-medium ${bt.total_return >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                    {(bt.total_return * 100).toFixed(2)}%
                  </td>
                  <td className="py-2 pr-3 text-rose-400">{(bt.max_drawdown * 100).toFixed(2)}%</td>
                  <td className="py-2 pr-3">{bt.trade_count}</td>
                  <td className="py-2 pr-3">
                    <Badge tone={bt.status === "completed" ? "green" : "slate"}>{bt.status}</Badge>
                  </td>
                  <td className="py-2">
                    <Link href={`/backtests/${bt.backtest_id}`} className="text-sky-400 hover:underline">
                      {t("common.view")}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
