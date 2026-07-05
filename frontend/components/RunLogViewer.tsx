"use client";

import { useI18n } from "../lib/i18n";
import { Card, EmptyState } from "./ui";

export default function RunLogViewer({ logs, title }: { logs: string[]; title?: string }) {
  const { t } = useI18n();
  return (
    <Card title={title ?? t("backtests.logs")}>
      {logs.length === 0 ? (
        <EmptyState label={t("common.empty")} />
      ) : (
        <pre className="max-h-64 overflow-auto rounded-lg bg-surface p-3 text-xs leading-relaxed text-slate-400">
          {logs.join("\n")}
        </pre>
      )}
    </Card>
  );
}
