"use client";

import { useI18n, type Language } from "../lib/i18n";

export default function LanguageSwitcher() {
  const { lang, setLang } = useI18n();
  const options: { value: Language; label: string }[] = [
    { value: "en", label: "EN" },
    { value: "zh-CN", label: "中文" },
  ];
  return (
    <div
      className="flex items-center gap-1 rounded-lg border border-edge bg-panel p-0.5"
      data-testid="language-switcher"
    >
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => setLang(opt.value)}
          className={`rounded-md px-2 py-1 text-xs font-medium transition ${
            lang === opt.value ? "bg-sky-600 text-white" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
