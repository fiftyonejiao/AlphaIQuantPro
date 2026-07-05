"use client";

import { useState } from "react";
import { useI18n } from "../lib/i18n";
import { Field, inputClass } from "./ui";
import BacktestRunButton from "./BacktestRunButton";

export interface BacktestFormValues {
  symbol: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  fee_rate: number;
  slippage: number;
  position_size: number;
}

const DEFAULTS: BacktestFormValues = {
  symbol: "AAPL",
  timeframe: "1d",
  start_date: "2023-01-01",
  end_date: "2024-06-30",
  initial_capital: 100000,
  fee_rate: 0.001,
  slippage: 0.0005,
  position_size: 1.0,
};

export default function BacktestConfigForm({
  onRun,
  running,
}: {
  onRun: (values: BacktestFormValues) => void;
  running: boolean;
}) {
  const { t } = useI18n();
  const [values, setValues] = useState<BacktestFormValues>(DEFAULTS);

  const set = <K extends keyof BacktestFormValues>(key: K, value: BacktestFormValues[K]) =>
    setValues((prev) => ({ ...prev, [key]: value }));

  return (
    <div className="space-y-3" data-testid="backtest-config-form">
      <div className="grid grid-cols-2 gap-3">
        <Field label={t("common.symbol")}>
          <input className={inputClass} value={values.symbol} onChange={(e) => set("symbol", e.target.value)} />
        </Field>
        <Field label={t("common.timeframe")}>
          <select className={inputClass} value={values.timeframe} onChange={(e) => set("timeframe", e.target.value)}>
            <option value="1d">1d</option>
            <option value="1h">1h</option>
            <option value="15m">15m</option>
          </select>
        </Field>
        <Field label={t("backtests.startDate")}>
          <input type="date" className={inputClass} value={values.start_date} onChange={(e) => set("start_date", e.target.value)} />
        </Field>
        <Field label={t("backtests.endDate")}>
          <input type="date" className={inputClass} value={values.end_date} onChange={(e) => set("end_date", e.target.value)} />
        </Field>
        <Field label={t("backtests.initialCapital")}>
          <input type="number" className={inputClass} value={values.initial_capital} onChange={(e) => set("initial_capital", Number(e.target.value))} />
        </Field>
        <Field label={t("backtests.positionSize")}>
          <input type="number" step="0.1" min="0.1" max="1" className={inputClass} value={values.position_size} onChange={(e) => set("position_size", Number(e.target.value))} />
        </Field>
        <Field label={t("backtests.feeRate")}>
          <input type="number" step="0.0001" className={inputClass} value={values.fee_rate} onChange={(e) => set("fee_rate", Number(e.target.value))} />
        </Field>
        <Field label={t("backtests.slippage")}>
          <input type="number" step="0.0001" className={inputClass} value={values.slippage} onChange={(e) => set("slippage", Number(e.target.value))} />
        </Field>
      </div>
      <BacktestRunButton onClick={() => onRun(values)} running={running} />
    </div>
  );
}
