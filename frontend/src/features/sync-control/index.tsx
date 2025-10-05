import { useEffect, useMemo, useState } from "react";
import { Loader2, RefreshCw, WifiOff, Wifi } from "lucide-react";

import { useOffline } from "../../app/providers/OfflineProvider";
import { createId } from "../../shared/lib/createId";

type Toast = { id: string; message: string; tone: "info" | "success" | "error" };

export function SyncControl({ variant = "panel" }: { variant?: "panel" | "inline" }) {
  const { status, queueSize, syncNow, lastSyncAt } = useOffline();
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    if (status === "offline") {
      pushToast("error", "Нет сети. Запросы будут поставлены в очередь.");
    } else if (status === "queued") {
      pushToast("info", `В очереди ${queueSize} действий. Нажмите синхронизацию.`);
    } else if (status === "syncing") {
      pushToast("info", "Синхронизация...");
    } else if (status === "online" && queueSize === 0) {
      pushToast("success", "Все данные синхронизированы");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, queueSize]);

  function pushToast(tone: Toast["tone"], message: string) {
    const id = createId();
    setToasts((prev) => [...prev, { id, tone, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, 4000);
  }

  const statusLabel = useMemo(() => {
    switch (status) {
      case "offline":
        return "Оффлайн";
      case "queued":
        return `В очереди ${queueSize}`;
      case "syncing":
        return "Синхронизация";
      default:
        return "Онлайн";
    }
  }, [queueSize, status]);

  const Icon = status === "offline" ? WifiOff : status === "online" ? Wifi : RefreshCw;

  const content = (
    <button
      onClick={() => void syncNow()}
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium transition ${
        status === "offline" ? "border-red-300 bg-red-50 text-red-700" : "border-emerald-300 bg-emerald-50 text-emerald-700"
      }`}
    >
      {status === "syncing" ? <Loader2 size={14} className="animate-spin" /> : <Icon size={14} />}
      {statusLabel}
      {lastSyncAt ? <span className="text-[10px] text-emerald-700/70">{new Date(lastSyncAt).toLocaleTimeString()}</span> : null}
    </button>
  );

  return (
    <div className={variant === "panel" ? "flex flex-col gap-2" : "relative"}>
      {variant === "panel" ? (
        <div className="rounded-3xl bg-white p-4 shadow-sm shadow-slate-200">
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold text-slate-600">Синхронизация</div>
            {content}
          </div>
          <p className="mt-2 text-xs text-slate-500">
            Offline-first: данные сохраняются локально и отправляются при появлении сети.
          </p>
        </div>
      ) : (
        content
      )}
      <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-full max-w-xs flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto rounded-2xl px-4 py-3 text-sm shadow-lg shadow-slate-900/20 ${
              toast.tone === "error"
                ? "border border-red-400 bg-red-50 text-red-700"
                : toast.tone === "success"
                  ? "border border-emerald-400 bg-emerald-50 text-emerald-700"
                  : "border border-slate-300 bg-white text-slate-700"
            }`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  );
}
