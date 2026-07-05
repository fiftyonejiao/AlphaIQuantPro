"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import BacktestConfigForm, { type BacktestFormValues } from "../../../components/BacktestConfigForm";
import StrategyAIAssistantPanel from "../../../components/StrategyAIAssistantPanel";
import StrategyForm from "../../../components/StrategyForm";
import { Card, ErrorNote, Spinner } from "../../../components/ui";
import { api } from "../../../lib/api";
import { useI18n } from "../../../lib/i18n";
import type { BacktestResult, Strategy } from "../../../lib/types";

export default function StrategyDetailPage() {
  const { t } = useI18n();
  const params = useParams<{ strategyId: string }>();
  const router = useRouter();
  const [strategy, setStrategy] = useState<Strategy | null | undefined>(undefined);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<Strategy>(`/api/strategies/${params.strategyId}`)
      .then(setStrategy)
      .catch(() => setStrategy(null));
  }, [params.strategyId]);

  const runBacktest = async (values: BacktestFormValues) => {
    setError("");
    setRunning(true);
    try {
      const result = await api.post<BacktestResult>("/api/backtests", {
        strategy_id: params.strategyId,
        ...values,
      });
      router.push(`/backtests/${result.backtest_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
      setRunning(false);
    }
  };

  if (strategy === undefined) return <Spinner label={t("common.loading")} />;
  if (strategy === null) return <ErrorNote message={t("strategies.notFound")} />;

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold">{strategy.name}</h1>
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <StrategyForm existing={strategy} />
        </div>
        <div className="space-y-4">
          <Card title={t("backtests.config")}>
            <BacktestConfigForm onRun={runBacktest} running={running} />
            {error && <div className="mt-3"><ErrorNote message={error} /></div>}
          </Card>
          <StrategyAIAssistantPanel strategyId={strategy.strategy_id} />
        </div>
      </div>
    </div>
  );
}
