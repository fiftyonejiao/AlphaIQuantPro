"use client";

import { useEffect, useState } from "react";
import MarketDataStatusCard from "../../components/MarketDataStatusCard";
import { Badge, Button, Card, EmptyState, ErrorNote, Field, inputClass, Spinner } from "../../components/ui";
import { api } from "../../lib/api";
import { useI18n } from "../../lib/i18n";
import type { MarketDataset, MarketDataStatus } from "../../lib/types";

interface Source {
  capability_id: string;
  name: string;
  category: string;
  description: string;
  provider: string;
}

export default function MarketDataPage() {
  const { t } = useI18n();
  const [status, setStatus] = useState<MarketDataStatus | null>(null);
  const [sources, setSources] = useState<Source[] | null>(null);
  const [symbol, setSymbol] = useState("AAPL");
  const [startDate, setStartDate] = useState("2024-01-01");
  const [endDate, setEndDate] = useState("2024-06-30");
  const [dataset, setDataset] = useState<MarketDataset | null>(null);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get<MarketDataStatus>("/api/market-data/status").then(setStatus).catch(() => setStatus(null));
    api
      .get<{ sources: Source[] }>("/api/market-data/sources")
      .then((r) => setSources(r.sources))
      .catch(() => setSources([]));
  }, []);

  const fetchData = async () => {
    setError("");
    setFetching(true);
    try {
      const result = await api.post<MarketDataset>("/api/market-data/fetch", {
        symbol,
        timeframe: "1d",
        start_date: startDate,
        end_date: endDate,
      });
      setDataset(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setFetching(false);
    }
  };

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold">{t("marketData.title")}</h1>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <MarketDataStatusCard status={status} />
        <Card title={t("marketData.sources")} className="lg:col-span-2">
          {sources === null ? (
            <Spinner label={t("common.loading")} />
          ) : sources.length === 0 ? (
            <EmptyState label={t("common.empty")} />
          ) : (
            <div className="space-y-2">
              {sources.map((s) => (
                <div key={s.capability_id} className="flex items-start justify-between rounded-lg bg-surface p-3 text-sm">
                  <div>
                    <div className="font-medium text-slate-200">{s.name}</div>
                    <div className="text-xs text-slate-500">{s.description}</div>
                  </div>
                  <Badge tone={s.provider === "qveris" ? "green" : "amber"}>{s.provider}</Badge>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <Card title={t("marketData.fetchPreview")}>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          <Field label={t("common.symbol")}>
            <input className={inputClass} value={symbol} onChange={(e) => setSymbol(e.target.value)} />
          </Field>
          <Field label={t("backtests.startDate")}>
            <input type="date" className={inputClass} value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </Field>
          <Field label={t("backtests.endDate")}>
            <input type="date" className={inputClass} value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </Field>
          <div className="flex items-end">
            <Button onClick={fetchData} disabled={fetching} className="w-full">
              {fetching ? t("marketData.fetching") : t("marketData.fetch")}
            </Button>
          </div>
        </div>
        {error && <div className="mt-3"><ErrorNote message={error} /></div>}
        {dataset && (
          <div className="mt-4 space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium">
                {dataset.meta.symbol} — {dataset.bars.length} {t("marketData.bars")}
              </span>
              <Badge tone={dataset.meta.is_mock ? "amber" : "green"}>
                {dataset.meta.is_mock ? t("common.mockData") : t("common.liveData")}
              </Badge>
              <span className="text-xs text-slate-500">
                {t("marketData.provider")}: {dataset.meta.provider}
              </span>
            </div>
            {dataset.meta.quality_notes.length > 0 && (
              <div className="text-xs text-slate-500">
                {t("marketData.qualityNotes")}: {dataset.meta.quality_notes.join("; ")}
              </div>
            )}
            <div className="max-h-64 overflow-auto">
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 bg-panel text-xs text-slate-500">
                  <tr>
                    <th className="pb-2 pr-3">{t("trades.time")}</th>
                    <th className="pb-2 pr-3">O</th>
                    <th className="pb-2 pr-3">H</th>
                    <th className="pb-2 pr-3">L</th>
                    <th className="pb-2 pr-3">C</th>
                    <th className="pb-2">V</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-edge">
                  {dataset.bars.slice(0, 100).map((bar, i) => (
                    <tr key={i}>
                      <td className="py-1 pr-3 text-slate-400">{bar.timestamp.slice(0, 10)}</td>
                      <td className="py-1 pr-3">{bar.open.toFixed(2)}</td>
                      <td className="py-1 pr-3">{bar.high.toFixed(2)}</td>
                      <td className="py-1 pr-3">{bar.low.toFixed(2)}</td>
                      <td className="py-1 pr-3">{bar.close.toFixed(2)}</td>
                      <td className="py-1 text-slate-500">{bar.volume.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
