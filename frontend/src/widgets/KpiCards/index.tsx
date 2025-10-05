import { TrendingUp, Target, Award } from "lucide-react";

export type KpiCard = {
  id: string;
  label: string;
  value: string;
  delta?: string;
  tone?: "positive" | "negative" | "neutral";
};

const ICONS = [TrendingUp, Target, Award];

export function KpiCards({ items }: { items: KpiCard[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item, index) => {
        const Icon = ICONS[index % ICONS.length];
        const tone =
          item.tone === "positive"
            ? "text-emerald-600"
            : item.tone === "negative"
              ? "text-rose-600"
              : "text-slate-500";
        return (
          <div key={item.id} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wide text-slate-500">
              <span>{item.label}</span>
              <Icon size={16} className={tone} />
            </div>
            <div className="mt-3 text-2xl font-semibold text-slate-900">{item.value}</div>
            {item.delta && (
              <div className={`mt-2 text-xs ${tone}`}>{item.delta}</div>
            )}
          </div>
        );
      })}
    </div>
  );
}
