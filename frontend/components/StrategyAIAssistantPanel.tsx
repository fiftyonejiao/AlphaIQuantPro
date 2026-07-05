"use client";

import { useState } from "react";
import { api } from "../lib/api";
import { useI18n } from "../lib/i18n";
import { Badge, Button, Card, inputClass, Spinner } from "./ui";

interface ChatTurn {
  role: "user" | "assistant";
  content: string;
  isMock?: boolean;
}

export default function StrategyAIAssistantPanel({ strategyId }: { strategyId?: string }) {
  const { t, lang } = useI18n();
  const [history, setHistory] = useState<ChatTurn[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  const send = async () => {
    const message = input.trim();
    if (!message || busy) return;
    setInput("");
    const next: ChatTurn[] = [...history, { role: "user", content: message }];
    setHistory(next);
    setBusy(true);
    try {
      const resp = await api.post<{ reply: string; is_mock: boolean }>("/api/analysis/assistant-chat", {
        strategy_id: strategyId,
        message,
        language: lang,
        history: history.map((h) => ({ role: h.role, content: h.content })),
      });
      setHistory([...next, { role: "assistant", content: resp.reply, isMock: resp.is_mock }]);
    } catch (err) {
      setHistory([...next, { role: "assistant", content: t("common.error"), isMock: true }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card title={t("analysis.assistant")} actions={<Badge tone="sky">DeepSeek</Badge>}>
      <div className="mb-3 max-h-72 space-y-2 overflow-auto">
        {history.map((turn, i) => (
          <div
            key={i}
            className={`rounded-lg p-2.5 text-sm ${
              turn.role === "user" ? "ml-8 bg-sky-900/40 text-sky-100" : "mr-8 bg-surface text-slate-300"
            }`}
          >
            <p className="whitespace-pre-wrap">{turn.content}</p>
            {turn.isMock && (
              <p className="mt-1 text-xs text-amber-500">{t("analysis.mockNotice")}</p>
            )}
          </div>
        ))}
        {busy && <Spinner label={t("common.loading")} />}
      </div>
      <div className="flex gap-2">
        <input
          className={inputClass}
          value={input}
          placeholder={t("analysis.assistantPlaceholder")}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <Button onClick={send} disabled={busy || !input.trim()}>
          {t("analysis.send")}
        </Button>
      </div>
    </Card>
  );
}
