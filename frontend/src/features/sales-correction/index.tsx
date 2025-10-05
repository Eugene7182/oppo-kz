import { FormEvent, useState } from "react";
import { AlertTriangle, Send } from "lucide-react";

export type CorrectionFormValues = { deltaQty: number; reason: string };

export function CorrectionForm({ onSubmit }: { onSubmit: (values: CorrectionFormValues) => void }) {
  const [values, setValues] = useState<CorrectionFormValues>({ deltaQty: 0, reason: "" });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-3xl border border-rose-200 bg-rose-50 p-6 text-sm text-rose-900">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide">
        <AlertTriangle size={14} /> Создать коррекцию
      </div>
      <label className="flex flex-col gap-1">
        <span className="text-[11px] uppercase tracking-wide">Δ Кол-во</span>
        <input
          type="number"
          value={values.deltaQty}
          onChange={(event) => setValues((prev) => ({ ...prev, deltaQty: Number(event.target.value) }))}
          className="rounded-xl border border-rose-200 bg-white px-3 py-2"
        />
      </label>
      <label className="flex flex-col gap-1">
        <span className="text-[11px] uppercase tracking-wide">Причина</span>
        <textarea
          value={values.reason}
          onChange={(event) => setValues((prev) => ({ ...prev, reason: event.target.value }))}
          className="h-24 rounded-xl border border-rose-200 bg-white px-3 py-2"
        />
      </label>
      <button
        type="submit"
        className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-rose-500 px-3 py-2 font-semibold text-white shadow"
      >
        <Send size={16} /> Отправить на апрув
      </button>
    </form>
  );
}
