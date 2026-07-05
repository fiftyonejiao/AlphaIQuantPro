"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useI18n } from "../lib/i18n";
import type { EquityPoint } from "../lib/types";
import { Card, EmptyState } from "./ui";

export default function DrawdownChart({ data }: { data: EquityPoint[] }) {
  const { t } = useI18n();
  if (!data.length) {
    return (
      <Card title={t("backtests.drawdown")}>
        <EmptyState label={t("common.empty")} />
      </Card>
    );
  }
  let peak = data[0].equity;
  const points = data.map((p) => {
    peak = Math.max(peak, p.equity);
    return {
      ts: p.timestamp.slice(0, 10),
      drawdown: peak > 0 ? -(((peak - p.equity) / peak) * 100) : 0,
    };
  });
  return (
    <Card title={t("backtests.drawdown")}>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={points} margin={{ top: 4, right: 8, bottom: 0, left: 8 }}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
            <XAxis dataKey="ts" tick={{ fill: "#64748b", fontSize: 11 }} minTickGap={40} />
            <YAxis
              tick={{ fill: "#64748b", fontSize: 11 }}
              tickFormatter={(v: number) => `${v.toFixed(1)}%`}
              width={60}
            />
            <Tooltip
              contentStyle={{ background: "#111a2e", border: "1px solid #1e293b", borderRadius: 8 }}
              labelStyle={{ color: "#94a3b8" }}
              formatter={(value) => [`${Number(value).toFixed(2)}%`, ""]}
            />
            <Area type="monotone" dataKey="drawdown" stroke="#f43f5e" fill="#f43f5e33" strokeWidth={1.5} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
