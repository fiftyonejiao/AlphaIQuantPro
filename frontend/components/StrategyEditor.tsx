"use client";

import { useI18n } from "../lib/i18n";
import type { StrategyType } from "../lib/types";

export default function StrategyEditor({
  code,
  onChange,
  strategyType,
}: {
  code: string;
  onChange: (code: string) => void;
  strategyType: StrategyType;
}) {
  const { t } = useI18n();
  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400">{t("strategies.editor")}</span>
        <span className="text-xs text-slate-500">
          {strategyType === "indicator" ? t("strategies.codeHintIndicator") : t("strategies.codeHintScript")}
        </span>
      </div>
      <textarea
        value={code}
        onChange={(e) => onChange(e.target.value)}
        spellCheck={false}
        rows={18}
        className="w-full rounded-lg border border-edge bg-surface p-3 font-mono text-sm leading-relaxed text-emerald-200 outline-none focus:border-sky-600"
        data-testid="strategy-editor"
      />
      <p className="mt-1 text-xs text-amber-500">{t("strategies.sandboxWarning")}</p>
    </div>
  );
}
