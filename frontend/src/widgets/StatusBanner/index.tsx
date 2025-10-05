import { WifiOff, UploadCloud, Wifi } from "lucide-react";

type Props = {
  status: "online" | "offline" | "queued" | "syncing";
  queueSize: number;
};

export function StatusBanner({ status, queueSize }: Props) {
  const tone =
    status === "offline"
      ? { bg: "bg-rose-50", border: "border-rose-200", text: "text-rose-700", icon: <WifiOff size={16} /> }
      : status === "queued"
        ? { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-700", icon: <UploadCloud size={16} /> }
        : { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", icon: <Wifi size={16} /> };

  const message =
    status === "offline"
      ? "Оффлайн: изменения попадут в очередь"
      : status === "queued"
        ? `В очереди ${queueSize} действий`
        : status === "syncing"
          ? "Синхронизация..."
          : "Онлайн";

  return (
    <div className={`border-y px-4 py-2 text-xs ${tone.bg} ${tone.border} ${tone.text}`}>
      <div className="mx-auto flex max-w-6xl items-center gap-2">
        {tone.icon}
        <span className="font-medium uppercase tracking-wide">{message}</span>
      </div>
    </div>
  );
}
