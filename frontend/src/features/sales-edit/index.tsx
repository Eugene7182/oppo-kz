import { useState } from "react";
import { Pencil, Save } from "lucide-react";

import type { Sale } from "../../entities/sale";

export function SalesInlineEdit({ sale, onSave }: { sale: Sale; onSave: (update: Partial<Sale>) => void }) {
  const [qty, setQty] = useState<number>(sale.qty);
  const [reason, setReason] = useState<string>("");

  return (
    <div className="space-y-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide">
        <Pencil size={14} /> Редактирование продажи
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        <label className="flex flex-col gap-1">
          <span className="text-[11px] uppercase tracking-wide">Количество</span>
          <input
            type="number"
            min={0}
            value={qty}
            onChange={(event) => setQty(Number(event.target.value))}
            className="rounded-xl border border-amber-200 bg-white px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-[11px] uppercase tracking-wide">Причина изменения</span>
          <input
            type="text"
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            placeholder="Например: корректировка остатков"
            className="rounded-xl border border-amber-200 bg-white px-3 py-2"
          />
        </label>
      </div>
      <button
        onClick={() => onSave({ qty, status: "submitted", version: sale.version + 1 })}
        className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-amber-500 px-3 py-2 font-semibold text-white shadow"
      >
        <Save size={16} /> Сохранить изменения
      </button>
    </div>
  );
}
