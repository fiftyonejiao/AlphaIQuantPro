"use client";

import { useEffect, useState } from "react";
import LanguageSwitcher from "../../components/LanguageSwitcher";
import { Badge, Button, Card, Field, inputClass, Spinner } from "../../components/ui";
import { api } from "../../lib/api";
import { useI18n } from "../../lib/i18n";
import type { AppSettings } from "../../lib/types";

export default function SettingsPage() {
  const { t } = useI18n();
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [symbol, setSymbol] = useState("AAPL");
  const [timeframe, setTimeframe] = useState("1d");
  const [capital, setCapital] = useState(100000);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get<AppSettings>("/api/settings").then((s) => {
      setSettings(s);
      setSymbol(String(s.values.default_symbol ?? "AAPL"));
      setTimeframe(String(s.values.default_timeframe ?? "1d"));
      setCapital(Number(s.values.default_initial_capital ?? 100000));
    });
  }, []);

  const save = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await api.put("/api/settings", {
        values: {
          default_symbol: symbol,
          default_timeframe: timeframe,
          default_initial_capital: capital,
        },
      });
      setSaved(true);
    } finally {
      setSaving(false);
    }
  };

  if (!settings) return <Spinner label={t("common.loading")} />;

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold">{t("settings.title")}</h1>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title={t("settings.defaults")}>
          <div className="space-y-3">
            <Field label={t("settings.defaultSymbol")}>
              <input className={inputClass} value={symbol} onChange={(e) => setSymbol(e.target.value)} />
            </Field>
            <Field label={t("settings.defaultTimeframe")}>
              <select className={inputClass} value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
                <option value="1d">1d</option>
                <option value="1h">1h</option>
                <option value="15m">15m</option>
              </select>
            </Field>
            <Field label={t("settings.defaultCapital")}>
              <input type="number" className={inputClass} value={capital} onChange={(e) => setCapital(Number(e.target.value))} />
            </Field>
            <div className="flex items-center gap-3">
              <Button onClick={save} disabled={saving}>
                {t("common.save")}
              </Button>
              {saved && <span className="text-sm text-emerald-400">{t("settings.saved")}</span>}
            </div>
          </div>
        </Card>

        <div className="space-y-4">
          <Card title={t("common.language")}>
            <LanguageSwitcher />
          </Card>

          <Card title={t("settings.llm")}>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">{t("settings.llmModel")}</span>
                <span className="font-mono text-slate-300">{settings.deepseek.model}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">{t("common.status")}</span>
                <Badge tone={settings.deepseek.configured ? "green" : "amber"}>
                  {settings.deepseek.configured ? t("settings.llmConnected") : "MOCK"}
                </Badge>
              </div>
              {!settings.deepseek.configured && (
                <p className="text-xs text-amber-500">{t("settings.llmNotConfigured")}</p>
              )}
            </div>
          </Card>

          <Card title={t("settings.dataGateway")}>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">{t("common.status")}</span>
                <Badge tone={settings.qveris.configured ? "green" : "amber"}>
                  {settings.qveris.configured ? t("settings.qverisConnected") : "MOCK"}
                </Badge>
              </div>
              {!settings.qveris.configured && (
                <p className="text-xs text-amber-500">{t("settings.qverisNotConfigured")}</p>
              )}
            </div>
          </Card>

          <Card title={t("settings.liveTrading")}>
            <Badge tone="rose">{t("settings.liveTradingDisabled")}</Badge>
          </Card>
        </div>
      </div>

      <p className="text-xs text-slate-600">{t("settings.envNote")}</p>
      <p className="text-xs text-slate-600">{t("app.disclaimer")}</p>
    </div>
  );
}
