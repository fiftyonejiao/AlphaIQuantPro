"use client";

import { useI18n } from "../lib/i18n";
import type { Trade } from "../lib/types";
import { Badge, Card, EmptyState } from "./ui";

export default function TradeTable({ trades }: { trades: Trade[] }) {
  const { t } = useI18n();
  return (
    <Card title={t("backtests.trades")}>
      {trades.length === 0 ? (
        <EmptyState label={t("common.empty")} />
      ) : (
        <div className="max-h-80 overflow-auto">
          <table className="w-full text-left text-sm">
            <thead className="sticky top-0 bg-panel text-xs text-slate-500">
              <tr>
                <th className="pb-2 pr-3">{t("trades.time")}</th>
                <th className="pb-2 pr-3">{t("trades.side")}</th>
                <th className="pb-2 pr-3">{t("trades.quantity")}</th>
                <th className="pb-2 pr-3">{t("trades.price")}</th>
                <th className="pb-2 pr-3">{t("trades.fee")}</th>
                <th className="pb-2">{t("trades.reason")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-edge">
              {trades.map((trade, i) => (
                <tr key={i}>
                  <td className="py-1.5 pr-3 text-slate-400">{trade.timestamp.slice(0, 10)}</td>
                  <td className="py-1.5 pr-3">
                    <Badge tone={trade.side === "buy" ? "green" : "rose"}>
                      {trade.side === "buy" ? t("trades.buy") : t("trades.sell")}
                    </Badge>
                  </td>
                  <td className="py-1.5 pr-3">{trade.quantity.toFixed(4)}</td>
                  <td className="py-1.5 pr-3">{trade.price.toFixed(2)}</td>
                  <td className="py-1.5 pr-3 text-slate-400">{trade.fee.toFixed(2)}</td>
                  <td className="py-1.5 text-xs text-slate-500">{trade.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
