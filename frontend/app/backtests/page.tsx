"use client";

import { useEffect, useState } from "react";
import BacktestComparisonTable from "../../components/BacktestComparisonTable";
import { Spinner } from "../../components/ui";
import { api } from "../../lib/api";
import { useI18n } from "../../lib/i18n";
import type { BacktestSummary } from "../../lib/types";

export default function BacktestsPage() {
  const { t } = useI18n();
  const [backtests, setBacktests] = useState<BacktestSummary[] | null>(null);

  useEffect(() => {
    api.get<BacktestSummary[]>("/api/backtests").then(setBacktests).catch(() => setBacktests([]));
  }, []);

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold">{t("backtests.title")}</h1>
      {backtests === null ? (
        <Spinner label={t("common.loading")} />
      ) : (
        <BacktestComparisonTable backtests={backtests} />
      )}
    </div>
  );
}
