"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { I18nProvider, useI18n } from "../lib/i18n";
import DeepSeekStatusBadge from "./DeepSeekStatusBadge";
import LanguageSwitcher from "./LanguageSwitcher";

const NAV_ITEMS = [
  { href: "/dashboard", key: "nav.dashboard" },
  { href: "/strategies", key: "nav.strategies" },
  { href: "/backtests", key: "nav.backtests" },
  { href: "/paper-runs", key: "nav.paperRuns" },
  { href: "/market-data", key: "nav.marketData" },
  { href: "/analysis", key: "nav.analysis" },
  { href: "/settings", key: "nav.settings" },
];

function Shell({ children }: { children: React.ReactNode }) {
  const { t } = useI18n();
  const pathname = usePathname();
  return (
    <div className="flex min-h-screen">
      <aside className="fixed inset-y-0 flex w-52 flex-col border-r border-edge bg-panel">
        <div className="px-4 py-5">
          <Link href="/dashboard" className="text-lg font-bold text-sky-400">
            {t("app.name")}
          </Link>
          <p className="mt-1 text-xs text-slate-500">{t("app.tagline")}</p>
        </div>
        <nav className="flex-1 space-y-0.5 px-2">
          {NAV_ITEMS.map((item) => {
            const active = pathname?.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-lg px-3 py-2 text-sm font-medium transition ${
                  active ? "bg-sky-600/20 text-sky-300" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`}
              >
                {t(item.key)}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-edge p-3">
          <p className="text-[10px] leading-snug text-slate-600">{t("app.disclaimer")}</p>
        </div>
      </aside>
      <div className="ml-52 flex flex-1 flex-col">
        <header className="sticky top-0 z-10 flex items-center justify-end gap-3 border-b border-edge bg-surface/90 px-6 py-3 backdrop-blur">
          <DeepSeekStatusBadge />
          <LanguageSwitcher />
        </header>
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <I18nProvider>
      <Shell>{children}</Shell>
    </I18nProvider>
  );
}
