import { useState } from "react";
import { MailPlus, Copy } from "lucide-react";

import { InviteForm, InviteFormValues } from "../../../features/invites";
import { createId } from "../../../shared/lib/createId";

const mockInvites = [
  { id: "inv-1", email: "new.promoter@oppo.kz", role: "promoter", code: "PROMO-2024", expiresAt: "2024-10-31" },
  { id: "inv-2", email: "supervisor.west@oppo.kz", role: "supervisor", code: "SUP-ALM", expiresAt: "2024-09-30" },
];

export function AdminInvitesPage() {
  const [invites, setInvites] = useState(mockInvites);

  function handleSubmit(values: InviteFormValues) {
    const code = `${values.role.toUpperCase()}-${Math.random().toString(36).slice(2, 6)}`;
    setInvites((prev) => [{ id: createId(), email: values.email, role: values.role, code, expiresAt: "2024-12-31" }, ...prev]);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800">Инвайты</h1>
          <p className="text-sm text-slate-500">Приглашения для промоутеров и супервизоров. Код копируется в буфер.</p>
        </div>
        <MailPlus size={24} className="text-slate-400" />
      </div>
      <InviteForm onSubmit={handleSubmit} />
      <div className="grid gap-3 sm:grid-cols-2">
        {invites.map((invite) => (
          <div key={invite.id} className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="text-sm font-semibold text-slate-700">{invite.email}</div>
            <div className="text-xs text-slate-500">Роль: {invite.role}</div>
            <div className="mt-2 flex items-center justify-between rounded-2xl bg-slate-100 px-3 py-2 text-sm">
              <span>{invite.code}</span>
              <button
                onClick={() => navigator.clipboard.writeText(invite.code)}
                className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white px-2 py-1 text-xs"
              >
                <Copy size={12} /> Копировать
              </button>
            </div>
            <div className="mt-2 text-xs text-slate-400">Истекает: {invite.expiresAt}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
