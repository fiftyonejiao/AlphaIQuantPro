"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../lib/api";
import { useI18n } from "../lib/i18n";
import type { Strategy, StrategyType } from "../lib/types";
import StrategyEditor from "./StrategyEditor";
import StrategyParameterPanel from "./StrategyParameterPanel";
import { Button, Card, ErrorNote, Field, inputClass } from "./ui";

const DEFAULT_INDICATOR_CODE = `def generate_signals(df, params):
    """Return a Series of 1 (long) / 0 (flat) per bar."""
    fast = df["close"].rolling(int(params.get("fast_period", 10))).mean()
    slow = df["close"].rolling(int(params.get("slow_period", 30))).mean()
    return (fast > slow).astype(int).fillna(0)
`;

const DEFAULT_SCRIPT_CODE = `class Strategy:
    """Event-driven strategy: on_bar returns 1 (long) / 0 (flat)."""

    def on_start(self, ctx):
        ctx.state["closes"] = []

    def on_bar(self, ctx, bar):
        closes = ctx.state["closes"]
        closes.append(bar["close"])
        if len(closes) < 20:
            return 0
        avg = sum(closes[-20:]) / 20
        return 1 if bar["close"] > avg else 0
`;

export default function StrategyForm({ existing }: { existing?: Strategy }) {
  const { t } = useI18n();
  const router = useRouter();
  const [name, setName] = useState(existing?.name ?? "");
  const [description, setDescription] = useState(existing?.description ?? "");
  const [strategyType, setStrategyType] = useState<StrategyType>(existing?.strategy_type ?? "indicator");
  const [code, setCode] = useState(existing?.code ?? DEFAULT_INDICATOR_CODE);
  const [parameters, setParameters] = useState<Record<string, unknown>>(
    existing?.parameters ?? { fast_period: 10, slow_period: 30 }
  );
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const changeType = (next: StrategyType) => {
    setStrategyType(next);
    if (!existing) {
      setCode(next === "indicator" ? DEFAULT_INDICATOR_CODE : DEFAULT_SCRIPT_CODE);
    }
  };

  const save = async () => {
    setError("");
    setSaving(true);
    setSaved(false);
    try {
      const payload = { name, description, strategy_type: strategyType, code, parameters };
      if (existing) {
        await api.put(`/api/strategies/${existing.strategy_id}`, payload);
        setSaved(true);
      } else {
        const created = await api.post<Strategy>("/api/strategies", payload);
        router.push(`/strategies/${created.strategy_id}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card>
      <div className="space-y-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <Field label={t("common.name")}>
            <input className={inputClass} value={name} onChange={(e) => setName(e.target.value)} data-testid="strategy-name" />
          </Field>
          <Field label={t("common.description")}>
            <input className={inputClass} value={description} onChange={(e) => setDescription(e.target.value)} />
          </Field>
          <Field label={t("common.type")}>
            <select className={inputClass} value={strategyType} onChange={(e) => changeType(e.target.value as StrategyType)}>
              <option value="indicator">{t("strategies.typeIndicator")}</option>
              <option value="script">{t("strategies.typeScript")}</option>
            </select>
          </Field>
        </div>
        <StrategyEditor code={code} onChange={setCode} strategyType={strategyType} />
        <StrategyParameterPanel parameters={parameters} onChange={setParameters} />
        {error && <ErrorNote message={error} />}
        <div className="flex items-center gap-3">
          <Button onClick={save} disabled={saving || !name.trim()}>
            {t("common.save")}
          </Button>
          {saved && <span className="text-sm text-emerald-400">{t("strategies.saved")}</span>}
        </div>
      </div>
    </Card>
  );
}
