"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import BacktestComparisonTable from "../../components/BacktestComparisonTable";
import MarketDataStatusCard from "../../components/MarketDataStatusCard";
import { Button, Card, Spinner } from "../../components/ui";
import { api } from "../../lib/api";
import { useI18n } from "../../lib/i18n";
import type { BacktestSummary, MarketDataStatus, PaperRunState, Strategy } from "../../lib/types";

export default function DashboardPage() {
  const { t } = useI18n();
  const [strategies, setStrategies] = useState<Strategy[] | null>(null);
  const [backtests, setBacktests] = useState<BacktestSummary[] | null>(null);
  const [runs, setRuns] = useState<PaperRunState[] | null>(null);
  const [mdStatus, setMdStatus] = useState<MarketDataStatus | null>(null);

  useEffect(() => {
    api.get<Strategy[]>("/api/strategies").then(setStrategies).catch(() => setStrategies([]));
    api.get<BacktestSummary[]>("/api/backtests").then(setBacktests).catch(() => setBacktests([]));
    api.get<PaperRunState[]>("/api/paper-runs").then(setRuns).catch(() => setRuns([]));
    api.get<MarketDataStatus>("/api/market-data/status").then(setMdStatus).catch(() => setMdStatus(null));
  }, []);

  const loading = strategies === null || backtests === null || runs === null;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">{t("dashboard.title")}</h1>
          <p className="text-sm text-slate-500">{t("dashboard.subtitle")}</p>
        </div>
        <Link href="/strategies/new">
          <Button>{t("dashboard.newStrategy")}</Button>
        </Link>
      </div>

      {loading ? (
        <Spinner label={t("common.loading")} />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {[
              { label: t("dashboard.strategies"), value: strategies!.length, href: "/strategies" },
              { label: t("dashboard.backtests"), value: backtests!.length, href: "/backtests" },
              { label: t("dashboard.paperRuns"), value: runs!.length, href: "/paper-runs" },
            ].map((stat) => (
              <Link key={stat.href} href={stat.href}>
                <Card className="transition hover:border-sky-800">
                  <div className="text-xs text-slate-500">{stat.label}</div>
                  <div className="mt-1 text-3xl font-bold text-slate-100">{stat.value}</div>
                </Card>
              </Link>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <BacktestComparisonTable backtests={backtests!.slice(0, 8)} />
            </div>
            <div className="space-y-4">
              <MarketDataStatusCard status={mdStatus} />
              <Card title={t("dashboard.quickStart")}>
                <p className="text-sm text-slate-400">{t("dashboard.quickStartText")}</p>
              </Card>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
