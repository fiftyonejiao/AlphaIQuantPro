"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Badge, Button, Card, EmptyState, Spinner } from "../../components/ui";
import { api } from "../../lib/api";
import { useI18n } from "../../lib/i18n";
import type { Strategy } from "../../lib/types";

export default function StrategiesPage() {
  const { t } = useI18n();
  const [strategies, setStrategies] = useState<Strategy[] | null>(null);

  const load = () => api.get<Strategy[]>("/api/strategies").then(setStrategies).catch(() => setStrategies([]));

  useEffect(() => {
    load();
  }, []);

  const remove = async (id: string) => {
    if (!window.confirm(t("common.confirmDelete"))) return;
    await api.del(`/api/strategies/${id}`);
    load();
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("strategies.title")}</h1>
        <Link href="/strategies/new">
          <Button>{t("strategies.new")}</Button>
        </Link>
      </div>

      {strategies === null ? (
        <Spinner label={t("common.loading")} />
      ) : strategies.length === 0 ? (
        <EmptyState label={t("common.empty")} />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {strategies.map((s) => (
            <Card key={s.strategy_id}>
              <div className="flex items-start justify-between gap-2">
                <Link href={`/strategies/${s.strategy_id}`} className="font-semibold text-sky-300 hover:underline">
                  {s.name}
                </Link>
                <Badge tone={s.strategy_type === "indicator" ? "sky" : "green"}>
                  {s.strategy_type === "indicator" ? t("strategies.typeIndicator") : t("strategies.typeScript")}
                </Badge>
              </div>
              <p className="mt-2 line-clamp-2 min-h-10 text-sm text-slate-500">{s.description}</p>
              <div className="mt-3 flex items-center justify-between">
                <span className="text-xs text-slate-600">{s.created_at.slice(0, 10)}</span>
                <div className="flex gap-2">
                  <Link href={`/strategies/${s.strategy_id}`}>
                    <Button variant="secondary">{t("common.edit")}</Button>
                  </Link>
                  <Button variant="danger" onClick={() => remove(s.strategy_id)}>
                    {t("common.delete")}
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
