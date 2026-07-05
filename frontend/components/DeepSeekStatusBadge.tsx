"use client";

import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useI18n } from "../lib/i18n";
import type { AppSettings } from "../lib/types";
import { Badge } from "./ui";

export default function DeepSeekStatusBadge() {
  const { t } = useI18n();
  const [status, setStatus] = useState<AppSettings["deepseek"] | null>(null);

  useEffect(() => {
    api
      .get<AppSettings>("/api/settings")
      .then((s) => setStatus(s.deepseek))
      .catch(() => setStatus(null));
  }, []);

  if (!status) return null;
  return (
    <Badge tone={status.configured ? "green" : "amber"}>
      DeepSeek · {status.model} · {status.configured ? t("settings.llmConnected") : "MOCK"}
    </Badge>
  );
}
