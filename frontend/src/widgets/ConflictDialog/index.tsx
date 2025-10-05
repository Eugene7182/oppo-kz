import { ReactNode } from "react";
import { AlertTriangle, Server, Laptop } from "lucide-react";

import { ModalSheet } from "../ModalSheet";

export type ConflictPayload<T> = {
  server: T;
  local: T;
  onResolve: (mode: "overwrite" | "accept-server") => void;
};

export function ConflictDialog<T extends { id: string }>({ open, title, payload, render }: { open: boolean; title: string; payload: ConflictPayload<T> | null; render: (item: T) => ReactNode }) {
  if (!payload) return null;

  return (
    <ModalSheet open={open} onClose={() => payload.onResolve("accept-server")} title={title}>
      <div className="space-y-4 text-sm">
        <div className="flex items-center gap-2 rounded-2xl bg-amber-50 px-3 py-2 text-amber-700">
          <AlertTriangle size={16} /> Версия на сервере изменилась. Выберите действие.
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 p-3">
            <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase text-slate-500">
              <Server size={14} /> Сервер
            </div>
            {render(payload.server)}
          </div>
          <div className="rounded-2xl border border-slate-200 p-3">
            <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase text-slate-500">
              <Laptop size={14} /> Локально
            </div>
            {render(payload.local)}
          </div>
        </div>
        <div className="grid gap-2 sm:grid-cols-2">
          <button
            onClick={() => payload.onResolve("overwrite")}
            className="rounded-2xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white"
          >
            Перезаписать сервер
          </button>
          <button
            onClick={() => payload.onResolve("accept-server")}
            className="rounded-2xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-600"
          >
            Принять серверную версию
          </button>
        </div>
      </div>
    </ModalSheet>
  );
}
