import { useState } from "react";
import { CalendarCheck } from "lucide-react";

export function PeriodClosePanel({ periods, onClose }: { periods: string[]; onClose: (id: string) => void }) {
  const [selected, setSelected] = useState<string>(periods[0] ?? "");

  return (
    <div className="space-y-3 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        <CalendarCheck size={14} /> Закрытие периода
      </div>
      <select
        value={selected}
        onChange={(event) => setSelected(event.target.value)}
        className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
      >
        {periods.map((period) => (
          <option key={period} value={period}>
            {period}
          </option>
        ))}
      </select>
      <button
        onClick={() => onClose(selected)}
        className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow"
      >
        Подтвердить закрытие
      </button>
      <p className="text-xs text-slate-500">
        Период закрывается без блокировки предыдущих данных. При попытке редактирования появляется форма коррекции.
      </p>
    </div>
  );
}
