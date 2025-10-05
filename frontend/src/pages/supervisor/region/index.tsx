import { useMemo, useState } from "react";
import { Trophy, Users, ListPlus } from "lucide-react";

import { FilterBar, FilterState } from "../../../widgets/FilterBar";
import { KpiCards } from "../../../widgets/KpiCards";
import { ResponsiveTable, Column } from "../../../widgets/ResponsiveTable";
import { ChartPlaceholder } from "../../../widgets/ChartPlaceholder";
import { InviteForm, InviteFormValues } from "../../../features/invites";
import { SalesInlineEdit } from "../../../features/sales-edit";
import { SyncControl } from "../../../features/sync-control";
import { salesMock } from "../../../entities/sale/mock";
import { products } from "../../../entities/product/mock";
import { dictionariesMock } from "../../../entities/dict/mock";

export function SupervisorRegionPage() {
  const [filters, setFilters] = useState<FilterState | null>(null);
  const [editing, setEditing] = useState<string | null>(null);
  const [teamSales, setTeamSales] = useState(salesMock);

  const stores = dictionariesMock.stores;

  const kpis = useMemo(
    () => [
      { id: "region-kpi", label: "KPI региона", value: "92%", delta: "+4% WoW", tone: "positive" as const },
      { id: "team", label: "Команда", value: `${teamSales.length} промоутеров`, tone: "neutral" as const },
      { id: "leader", label: "Лидер сети", value: "Sulpak", delta: "38% доля", tone: "neutral" as const },
      { id: "bonus", label: "Бонусы", value: "1.8 млн ₸", tone: "positive" as const },
    ],
    [teamSales.length],
  );

  const leaderboard = useMemo(() => {
    const byStore = new Map<string, { id: string; qty: number; amount: number; name: string }>();
    teamSales.forEach((sale) => {
      const current = byStore.get(sale.storeId) ?? { id: sale.storeId, qty: 0, amount: 0, name: sale.storeName };
      current.qty += sale.qty;
      current.amount += sale.amount;
      byStore.set(sale.storeId, current);
    });
    return Array.from(byStore.values()).sort((a, b) => b.amount - a.amount).slice(0, 5);
  }, [teamSales]);

  const columns: Column<typeof teamSales[number]>[] = [
    { key: "storeName", label: "Магазин" },
    { key: "skuName", label: "SKU" },
    { key: "qty", label: "Шт." },
    { key: "amount", label: "Сумма", render: (item) => `${item.amount.toLocaleString()} ₸` },
    { key: "soldAt", label: "Дата", render: (item) => new Date(item.soldAt).toLocaleDateString() },
  ];

  function handleInvite(values: InviteFormValues) {
    console.info("[demo] отправка инвайта", values);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold text-slate-800">Регион Алматы</h1>
          <p className="text-sm text-slate-500">Сводка по команде и магазинам. Фильтры применяются ко всем виджетам.</p>
        </div>
        <SyncControl variant="inline" />
      </div>
      <FilterBar products={products} onChange={(next) => setFilters(next)} />
      <KpiCards items={kpis} />

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartPlaceholder title="Plan vs Fact по команде" />
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-700">Топ магазинов</h2>
            <Trophy size={18} className="text-amber-500" />
          </div>
          <ul className="mt-4 space-y-2 text-sm text-slate-600">
            {leaderboard.map((item, index) => (
              <li key={item.id} className="flex items-center justify-between rounded-2xl bg-slate-50 px-3 py-2">
                <span className="font-medium text-slate-700">{index + 1}. {item.name}</span>
                <span>{item.qty} шт. · {item.amount.toLocaleString()} ₸</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[2fr,1fr]">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-700">Продажи команды</h2>
            <Users size={18} className="text-slate-400" />
          </div>
          <ResponsiveTable
            data={teamSales}
            columns={[...columns, { key: "id", label: "Действия", render: (item) => (
              <button
                onClick={() => setEditing(item.id)}
                className="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600"
              >
                <ListPlus size={12} /> Изменить
              </button>
            ) }]}
          />
          {editing && (
            <SalesInlineEdit
              sale={teamSales.find((sale) => sale.id === editing)!}
              onSave={(update) => {
                setTeamSales((prev) => prev.map((sale) => (sale.id === editing ? { ...sale, ...update } : sale)));
                setEditing(null);
              }}
            />
          )}
        </div>
        <div className="space-y-4">
          <InviteForm onSubmit={handleInvite} />
          <div className="rounded-3xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
            <div className="text-xs font-semibold uppercase text-slate-500">Примененные фильтры</div>
            <ul className="mt-2 space-y-1">
              <li>Scope: {filters?.scope ?? "all"}</li>
              <li>Metric: {filters?.metric ?? "qty"}</li>
              <li>Compare: {filters?.compare ?? "none"}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
