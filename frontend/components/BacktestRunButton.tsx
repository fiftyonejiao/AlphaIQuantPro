"use client";

import { useI18n } from "../lib/i18n";
import { Button, Spinner } from "./ui";

export default function BacktestRunButton({
  onClick,
  running,
}: {
  onClick: () => void;
  running: boolean;
}) {
  const { t } = useI18n();
  return (
    <div className="flex items-center gap-3">
      <Button onClick={onClick} disabled={running} className="px-5" >
        {running ? t("backtests.running") : t("backtests.runBacktest")}
      </Button>
      {running && <Spinner />}
    </div>
  );
}
