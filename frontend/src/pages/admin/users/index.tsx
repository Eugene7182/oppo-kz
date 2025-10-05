import { useMemo } from "react";
import { ShieldCheck } from "lucide-react";

import { KpiCards } from "../../../widgets/KpiCards";
import { ResponsiveTable, Column } from "../../../widgets/ResponsiveTable";
import { getAllMockUsers } from "../../../entities/user/mock";

export function AdminUsersPage() {
  const users = getAllMockUsers();
  const kpis = useMemo(
    () => [
      { id: "total", label: "Всего пользователей", value: `${users.length}` },
      { id: "admin", label: "Админов", value: `${users.filter((user) => user.role === "admin").length}` },
      { id: "field", label: "Поле", value: `${users.filter((user) => user.role === "promoter" || user.role === "supervisor").length}` },
      { id: "office", label: "Офис", value: `${users.filter((user) => user.role === "office").length}` },
    ],
    [users],
  );

  const columns: Column<(typeof users)[number]>[] = [
    { key: "fullName", label: "Имя" },
    { key: "email", label: "Email" },
    { key: "role", label: "Роль" },
    { key: "region", label: "Регион" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800">Пользователи</h1>
          <p className="text-sm text-slate-500">Управление доступом и ролями. SSO в отдельном бекенде.</p>
        </div>
        <ShieldCheck size={24} className="text-emerald-500" />
      </div>
      <KpiCards items={kpis} />
      <ResponsiveTable data={users.map((user) => ({ ...user, id: user.id }))} columns={columns} />
    </div>
  );
}
