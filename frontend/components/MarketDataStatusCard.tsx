"use client";

import { useI18n } from "../lib/i18n";
import type { MarketDataStatus } from "../lib/types";
import { Badge, Card } from "./ui";

export default function MarketDataStatusCard({ status }: { status: MarketDataStatus | null }) {
  const { t } = useI18n();
  if (!status) return null;
  return (
    <Card title={t("marketData.status")}>
      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-slate-500">{t("marketData.qverisConfigured")}</span>
          <Badge tone={status.qveris_configured ? "green" : "amber"}>
            {status.qveris_configured ? t("marketData.yes") : t("marketData.no")}
          </Badge>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-500">{t("marketData.qverisReachable")}</span>
          <Badge tone={status.qveris_reachable ? "green" : "amber"}>
            {status.qveris_reachable ? t("marketData.yes") : t("marketData.no")}
          </Badge>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-500">{t("marketData.activeSource")}</span>
          <Badge tone={status.active_source === "qveris" ? "green" : "amber"}>
            {status.active_source === "qveris" ? t("common.liveData") : t("common.mockData")}
          </Badge>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-500">{t("marketData.sessionId")}</span>
          <span className="font-mono text-xs text-slate-400">{status.session_id}</span>
        </div>
        {status.notes.map((note, i) => (
          <p key={i} className="text-xs text-slate-500">
            {note}
          </p>
        ))}
      </div>
    </Card>
  );
}
