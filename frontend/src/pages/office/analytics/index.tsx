import { useMemo, useState } from "react";
import { BarChart4, Network, Building2, Smartphone, Target, CalendarFold } from "lucide-react";

import { FilterBar, FilterState } from "../../../widgets/FilterBar";
import { ResponsiveTable, Column } from "../../../widgets/ResponsiveTable";
import { KpiCards } from "../../../widgets/KpiCards";
import { ChartPlaceholder } from "../../../widgets/ChartPlaceholder";
import { PlanBulkUpload } from "../../../features/plan-bulk";
import { PeriodClosePanel } from "../../../features/period-close";
import { SyncControl } from "../../../features/sync-control";
import { salesMock } from "../../../entities/sale/mock";
import { products } from "../../../entities/product/mock";
import { plansMock } from "../../../entities/plan/mock";
import { ActionableInsightsWidget } from "../../../widgets/ActionableInsights";
import { insightSampleRequest } from "../../../entities/insight/mock";
import { featureFlags } from "../../../shared/config/featureFlags";

const tabs = [
  { id: "all", label: "Все продажи", icon: BarChart4 },
  { id: "network", label: "По сетям", icon: Network },
  { id: "store", label: "По магазинам", icon: Building2 },
  { id: "models", label: "По моделям", icon: Smartphone },
  { id: "plan", label: "План vs Факт", icon: Target },
  { id: "close", label: "Закрытие периодов", icon: CalendarFold },
] as const;

type TabId = (typeof tabs)[number]["id"];

export function OfficeAnalyticsPage() {
  const [activeTab, setActiveTab] = useState<TabId>("all");
  const [filters, setFilters] = useState<FilterState | null>(null);

  const kpis = useMemo(
    () => [
      { id: "national-kpi", label: "KPI страны", value: "88%", delta: "+2% MoM", tone: "positive" as const },
      { id: "revenue", label: "Выручка", value: "5.2 млрд ₸", tone: "positive" as const },
      { id: "avg", label: "Avg чек", value: "165 000 ₸", tone: "neutral" as const },
      { id: "bonus", label: "Бонусы", value: "9.4 млн ₸", tone: "neutral" as const },
    ],
    [],
  );

  const salesColumns: Column<typeof salesMock[number]>[] = [
    { key: "network", label: "Сеть" },
    { key: "storeName", label: "Магазин" },
    { key: "skuName", label: "SKU" },
    { key: "qty", label: "Шт." },
    { key: "amount", label: "₸", render: (item) => item.amount.toLocaleString() },
  ];

  const plansColumns: Column<typeof plansMock[number]>[] = [
    { key: "ownerName", label: "Объект" },
    { key: "scope", label: "Scope" },
    { key: "target", label: "План" },
    { key: "achieved", label: "Факт" },
    { key: "period", label: "Период" },
  ];

  function renderTab() {
    switch (activeTab) {
      case "all":
        return <ResponsiveTable data={salesMock} columns={salesColumns} />;
      case "network":
        return <ChartPlaceholder title="Продажи по сетям" />;
      case "store":
        return <ChartPlaceholder title="Продажи по магазинам" />;
      case "models":
        return <ChartPlaceholder title="Топ SKU" />;
      case "plan":
        return (
          <div className="grid gap-4 lg:grid-cols-2">
            <ChartPlaceholder title="План vs Факт (₸)" />
            <ResponsiveTable data={plansMock} columns={plansColumns} />
          </div>
        );
      case "close":
        return (
          <div className="grid gap-4 lg:grid-cols-2">
            <PeriodClosePanel periods={["2024-07", "2024-08", "2024-09"]} onClose={(period) => console.info("close", period)} />
            <PlanBulkUpload onUpload={(file) => console.info("upload plans", file.name)} />
          </div>
        );
      default:
        return null;
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800">Аналитика страны</h1>
          <p className="text-sm text-slate-500">BI-фильтры управляют всеми виджетами. Offline-first: можно анализировать даже без сети.</p>
        </div>
        <SyncControl variant="inline" />
      </div>
      <FilterBar products={products} onChange={setFilters} />
      <KpiCards items={kpis} />
      {featureFlags.aiInsights && <ActionableInsightsWidget request={insightSampleRequest} />}
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium transition ${
              activeTab === tab.id ? "border-slate-900 bg-slate-900 text-white" : "border-slate-200 text-slate-600"
            }`}
          >
            <tab.icon size={16} /> {tab.label}
          </button>
        ))}
      </div>
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        {renderTab()}
      </div>
      <div className="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
        <div className="text-xs font-semibold uppercase text-slate-500">Активные фильтры</div>
        <p className="mt-2">Scope: {filters?.scope ?? "all"} · Metric: {filters?.metric ?? "qty"} · Compare: {filters?.compare ?? "none"}</p>
      </div>
    </div>
  );
}
