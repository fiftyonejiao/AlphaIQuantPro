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

export default function EquityCurveChart({ data }: { data: EquityPoint[] }) {
  const { t } = useI18n();
  if (!data.length) {
    return (
      <Card title={t("backtests.equityCurve")}>
        <EmptyState label={t("common.empty")} />
      </Card>
    );
  }
  const points = data.map((p) => ({ ...p, ts: p.timestamp.slice(0, 10) }));
  return (
    <Card title={t("backtests.equityCurve")}>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={points} margin={{ top: 4, right: 8, bottom: 0, left: 8 }}>
            <defs>
              <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#0ea5e9" stopOpacity={0.4} />
                <stop offset="100%" stopColor="#0ea5e9" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
            <XAxis dataKey="ts" tick={{ fill: "#64748b", fontSize: 11 }} minTickGap={40} />
            <YAxis
              tick={{ fill: "#64748b", fontSize: 11 }}
              domain={["auto", "auto"]}
              tickFormatter={(v: number) => v.toLocaleString()}
              width={80}
            />
            <Tooltip
              contentStyle={{ background: "#111a2e", border: "1px solid #1e293b", borderRadius: 8 }}
              labelStyle={{ color: "#94a3b8" }}
            />
            <Area type="monotone" dataKey="equity" stroke="#0ea5e9" fill="url(#equityFill)" strokeWidth={1.5} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
