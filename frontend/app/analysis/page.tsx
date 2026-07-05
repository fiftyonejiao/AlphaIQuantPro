"use client";

import { useEffect, useState } from "react";
import StrategyAIAssistantPanel from "../../components/StrategyAIAssistantPanel";
import { Button, Card, Field, inputClass, Spinner } from "../../components/ui";
import { api } from "../../lib/api";
import { useI18n } from "../../lib/i18n";
import type { BacktestSummary, Strategy } from "../../lib/types";

interface Review {
  review: string;
  is_mock: boolean;
  disclaimer: string;
}

export default function AnalysisPage() {
  const { t, lang } = useI18n();
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [backtests, setBacktests] = useState<BacktestSummary[]>([]);
  const [strategyId, setStrategyId] = useState("");
  const [backtestId, setBacktestId] = useState("");
  const [review, setReview] = useState<Review | null>(null);
  const [reviewing, setReviewing] = useState(false);

  useEffect(() => {
    api.get<Strategy[]>("/api/strategies").then((list) => {
      setStrategies(list);
      if (list.length > 0) setStrategyId(list[0].strategy_id);
    });
    api.get<BacktestSummary[]>("/api/backtests").then(setBacktests);
  }, []);

  const requestReview = async () => {
    setReviewing(true);
    try {
      const result = await api.post<Review>("/api/analysis/strategy-review", {
        strategy_id: strategyId,
        backtest_id: backtestId || null,
        language: lang,
      });
      setReview(result);
    } finally {
      setReviewing(false);
    }
  };

  const relevantBacktests = backtests.filter((b) => b.strategy_id === strategyId);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold">{t("analysis.title")}</h1>
        <p className="text-sm text-slate-500">{t("analysis.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <Card title={t("analysis.review")}>
          <div className="space-y-3">
            <Field label={t("analysis.selectStrategy")}>
              <select
                className={inputClass}
                value={strategyId}
                onChange={(e) => {
                  setStrategyId(e.target.value);
                  setBacktestId("");
                }}
              >
                {strategies.map((s) => (
                  <option key={s.strategy_id} value={s.strategy_id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label={t("analysis.selectBacktest")}>
              <select className={inputClass} value={backtestId} onChange={(e) => setBacktestId(e.target.value)}>
                <option value="">{t("analysis.noBacktest")}</option>
                {relevantBacktests.map((b) => (
                  <option key={b.backtest_id} value={b.backtest_id}>
                    {b.symbol} {b.start_date} → {b.end_date} ({(b.total_return * 100).toFixed(1)}%)
                  </option>
                ))}
              </select>
            </Field>
            <Button onClick={requestReview} disabled={reviewing || !strategyId}>
              {reviewing ? t("analysis.reviewing") : t("analysis.requestReview")}
            </Button>
            {reviewing && <Spinner />}
            {review && (
              <div className="space-y-2">
                <p className="whitespace-pre-wrap rounded-lg bg-surface p-3 text-sm text-slate-300">{review.review}</p>
                {review.is_mock && <p className="text-xs text-amber-500">{t("analysis.mockNotice")}</p>}
                <p className="text-xs text-slate-600">{review.disclaimer}</p>
              </div>
            )}
          </div>
        </Card>

        <StrategyAIAssistantPanel strategyId={strategyId || undefined} />
      </div>
    </div>
  );
}
