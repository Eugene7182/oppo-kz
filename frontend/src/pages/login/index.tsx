import { useState } from "react";
import { LogIn } from "lucide-react";

import { useAuth } from "../../app/providers/AuthProvider";
import type { UserRole } from "../../entities/user";

const roles: { role: UserRole; label: string; description: string }[] = [
  { role: "promoter", label: "Промоутер", description: "Дневной отчёт, бонусы и корректировки" },
  { role: "supervisor", label: "Супервизор", description: "KPI региона и команда" },
  { role: "office", label: "Офис", description: "Аналитика по стране" },
  { role: "admin", label: "Админ", description: "Пользователи и справочники" },
];

export function LoginByRole() {
  const { loginAs } = useAuth();
  const [selected, setSelected] = useState<UserRole | null>(null);

  return (
    <div className="flex min-h-screen flex-col justify-center bg-slate-950 px-4 py-12 text-white">
      <div className="mx-auto w-full max-w-md space-y-8 rounded-3xl bg-slate-900/40 p-8 shadow-xl shadow-slate-900/60">
        <div className="space-y-2 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-slate-700 px-3 py-1 text-xs uppercase tracking-wide">
            <LogIn size={14} /> Demo-login
          </div>
          <h1 className="text-2xl font-semibold">Выберите роль</h1>
          <p className="text-sm text-slate-300">
            Моки без бэкенда. Можно переключать роли, чтобы проверить разные сценарии.
          </p>
        </div>
        <div className="grid gap-3">
          {roles.map((role) => (
            <button
              key={role.role}
              onClick={() => {
                setSelected(role.role);
                loginAs(role.role);
              }}
              className={`rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-left transition hover:border-emerald-500/80 hover:bg-slate-900/80 ${
                selected === role.role ? "border-emerald-500" : ""
              }`}
            >
              <div className="text-base font-semibold">{role.label}</div>
              <div className="text-sm text-slate-400">{role.description}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
