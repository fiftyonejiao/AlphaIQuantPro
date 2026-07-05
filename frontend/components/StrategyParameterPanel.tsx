"use client";

import { useEffect, useState } from "react";
import { useI18n } from "../lib/i18n";

export default function StrategyParameterPanel({
  parameters,
  onChange,
}: {
  parameters: Record<string, unknown>;
  onChange: (params: Record<string, unknown>) => void;
}) {
  const { t } = useI18n();
  const [text, setText] = useState(JSON.stringify(parameters, null, 2));
  const [valid, setValid] = useState(true);

  useEffect(() => {
    setText(JSON.stringify(parameters, null, 2));
  }, [parameters]);

  const handleChange = (value: string) => {
    setText(value);
    try {
      const parsed = JSON.parse(value);
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        setValid(true);
        onChange(parsed as Record<string, unknown>);
        return;
      }
      setValid(false);
    } catch {
      setValid(false);
    }
  };

  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400">{t("strategies.parameters")}</span>
        <span className="text-xs text-slate-500">{t("strategies.parametersHint")}</span>
      </div>
      <textarea
        value={text}
        onChange={(e) => handleChange(e.target.value)}
        spellCheck={false}
        rows={6}
        className={`w-full rounded-lg border bg-surface p-3 font-mono text-sm text-sky-200 outline-none ${
          valid ? "border-edge focus:border-sky-600" : "border-rose-700"
        }`}
        data-testid="strategy-parameters"
      />
    </div>
  );
}
