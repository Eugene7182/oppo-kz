import { FormEvent, useState } from "react";
import { Send } from "lucide-react";

import type { UserRole } from "../../entities/user";

export type InviteFormValues = {
  role: UserRole;
  email: string;
  network?: string;
};

export function InviteForm({ onSubmit }: { onSubmit: (values: InviteFormValues) => void }) {
  const [values, setValues] = useState<InviteFormValues>({ role: "promoter", email: "" });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div>
        <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Роль</label>
        <select
          value={values.role}
          onChange={(event) => setValues((prev) => ({ ...prev, role: event.target.value as UserRole }))}
          className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
        >
          <option value="promoter">Промоутер</option>
          <option value="supervisor">Супервизор</option>
          <option value="office">Офис</option>
        </select>
      </div>
      <div>
        <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Email</label>
        <input
          type="email"
          value={values.email}
          required
          onChange={(event) => setValues((prev) => ({ ...prev, email: event.target.value }))}
          className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
          placeholder="name@oppo.kz"
        />
      </div>
      <div>
        <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Сеть (опционально)</label>
        <input
          type="text"
          value={values.network ?? ""}
          onChange={(event) => setValues((prev) => ({ ...prev, network: event.target.value }))}
          className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
          placeholder="Sulpak"
        />
      </div>
      <button
        type="submit"
        className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-600"
      >
        <Send size={16} /> Создать приглашение
      </button>
    </form>
  );
}
