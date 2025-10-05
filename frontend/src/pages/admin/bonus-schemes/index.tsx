import { bonusSchemesMock } from "../../../entities/bonus/mock";
import { ResponsiveTable, Column } from "../../../widgets/ResponsiveTable";
import { KpiCards } from "../../../widgets/KpiCards";

export function AdminBonusSchemesPage() {
  const schemes = bonusSchemesMock;
  const kpis = [
    { id: "total", label: "Схем", value: `${schemes.length}` },
    { id: "active", label: "Активные", value: `${schemes.filter((scheme) => !scheme.validTo).length}` },
    { id: "hybrid", label: "Hybrid", value: `${schemes.filter((scheme) => scheme.type === "hybrid").length}` },
  ];

  const columns: Column<(typeof schemes)[number]>[] = [
    { key: "name", label: "Название" },
    { key: "type", label: "Тип" },
    { key: "network", label: "Сеть" },
    { key: "skuId", label: "SKU" },
    { key: "validFrom", label: "Start" },
    { key: "validTo", label: "End" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-800">Бонусные схемы</h1>
        <p className="text-sm text-slate-500">Проценты и фиксированные выплаты промоутерам. Управление лимитами в backend.</p>
      </div>
      <KpiCards items={kpis} />
      <ResponsiveTable data={schemes.map((scheme) => ({ ...scheme, id: scheme.id }))} columns={columns} />
    </div>
  );
}
