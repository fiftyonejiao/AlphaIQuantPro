"use client";

import StrategyForm from "../../../components/StrategyForm";
import { useI18n } from "../../../lib/i18n";

export default function NewStrategyPage() {
  const { t } = useI18n();
  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold">{t("strategies.new")}</h1>
      <StrategyForm />
    </div>
  );
}
