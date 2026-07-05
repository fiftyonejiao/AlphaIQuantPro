"use client";

import React from "react";

export function Card({
  title,
  children,
  className = "",
  actions,
}: {
  title?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className={`rounded-xl border border-edge bg-panel p-4 ${className}`}>
      {(title || actions) && (
        <div className="mb-3 flex items-center justify-between gap-2">
          {title && <h3 className="text-sm font-semibold text-slate-300">{title}</h3>}
          {actions}
        </div>
      )}
      {children}
    </div>
  );
}

export function Button({
  children,
  onClick,
  variant = "primary",
  disabled,
  type = "button",
  className = "",
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "danger" | "ghost";
  disabled?: boolean;
  type?: "button" | "submit";
  className?: string;
}) {
  const styles: Record<string, string> = {
    primary: "bg-sky-600 hover:bg-sky-500 text-white",
    secondary: "bg-slate-700 hover:bg-slate-600 text-slate-100",
    danger: "bg-rose-700 hover:bg-rose-600 text-white",
    ghost: "bg-transparent hover:bg-slate-800 text-slate-300",
  };
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg px-3 py-1.5 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${styles[variant]} ${className}`}
    >
      {children}
    </button>
  );
}

export function Badge({
  children,
  tone = "slate",
}: {
  children: React.ReactNode;
  tone?: "slate" | "green" | "amber" | "rose" | "sky";
}) {
  const tones: Record<string, string> = {
    slate: "bg-slate-700/60 text-slate-300",
    green: "bg-emerald-900/60 text-emerald-300",
    amber: "bg-amber-900/60 text-amber-300",
    rose: "bg-rose-900/60 text-rose-300",
    sky: "bg-sky-900/60 text-sky-300",
  };
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${tones[tone]}`}>
      {children}
    </span>
  );
}

export function Field({
  label,
  children,
  hint,
}: {
  label: string;
  children: React.ReactNode;
  hint?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-slate-400">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-xs text-slate-500">{hint}</span>}
    </label>
  );
}

export const inputClass =
  "w-full rounded-lg border border-edge bg-surface px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-sky-600";

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-400">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-600 border-t-sky-500" />
      {label}
    </div>
  );
}

export function EmptyState({ label }: { label: string }) {
  return (
    <div className="rounded-lg border border-dashed border-edge p-8 text-center text-sm text-slate-500">
      {label}
    </div>
  );
}

export function ErrorNote({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-rose-900 bg-rose-950/50 px-3 py-2 text-sm text-rose-300">
      {message}
    </div>
  );
}
