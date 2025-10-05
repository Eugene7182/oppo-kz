import { LineChart } from "lucide-react";

export function ChartPlaceholder({ title }: { title: string }) {
  return (
    <div className="flex min-h-[200px] flex-col justify-center rounded-3xl border border-dashed border-slate-200 bg-white p-6 text-center text-slate-400">
      <LineChart size={32} className="mx-auto text-slate-300" />
      <span className="mt-3 text-sm font-semibold text-slate-500">{title}</span>
      <p className="mt-1 text-xs text-slate-400">Здесь будет график из backend /analytics после подключения.</p>
    </div>
  );
}
