import { useMemo, useState } from "react";
import { Pencil, Trash2, FileWarning } from "lucide-react";

import { SalesForm, SaleFormValues } from "../../../features/sales-form";
import { SalesInlineEdit } from "../../../features/sales-edit";
import { CorrectionForm, CorrectionFormValues } from "../../../features/sales-correction";
import { KpiCards } from "../../../widgets/KpiCards";
import { ResponsiveTable, Column } from "../../../widgets/ResponsiveTable";
import { ConflictDialog, ConflictPayload } from "../../../widgets/ConflictDialog";
import { SyncControl } from "../../../features/sync-control";
import { SalesMockWithId, usePromoterData } from "./usePromoterData";

export function PromoterHomePage() {
  const { sales, products, stores, bonusSummary, updateSale, deleteSale, addSale, corrections, addCorrection } = usePromoterData();
  const [editing, setEditing] = useState<SalesMockWithId | null>(null);
  const [correctionFor, setCorrectionFor] = useState<SalesMockWithId | null>(null);
  const [conflict, setConflict] = useState<ConflictPayload<SalesMockWithId> | null>(null);

  const kpiItems = useMemo(
    () => [
      { id: "bonus", label: "Бонус за месяц", value: `${bonusSummary.monthTotal.toLocaleString()} ₸`, tone: "positive" as const },
      { id: "plan", label: "План", value: `${bonusSummary.plan} шт.`, tone: "neutral" as const },
      { id: "fact", label: "Факт", value: `${bonusSummary.fact} шт.`, delta: `${bonusSummary.achv}%`, tone: bonusSummary.achv >= 100 ? "positive" : "negative" },
      { id: "avg", label: "Средний чек", value: `${bonusSummary.averageAmount.toLocaleString()} ₸`, tone: "neutral" as const },
    ],
    [bonusSummary],
  );

  const columns: Column<SalesMockWithId>[] = [
    { key: "storeName", label: "Магазин" },
    { key: "skuName", label: "Модель" },
    { key: "qty", label: "Шт." },
    { key: "amount", label: "Сумма", render: (item) => `${item.amount.toLocaleString()} ₸` },
    { key: "soldAt", label: "Дата", render: (item) => new Date(item.soldAt).toLocaleDateString() },
    { key: "status", label: "Статус", render: (item) => (item.status === "locked" ? "Закрыт" : "Черновик") },
  ];

  function handleEditSubmit(update: Partial<SalesMockWithId>) {
    if (!editing) return;
    const result = updateSale(editing.id, update);
    if (result?.type === "conflict") {
      setConflict({
        server: result.server,
        local: result.local,
        onResolve: (mode) => {
          if (mode === "overwrite") {
            updateSale(editing.id, { ...result.local, version: result.server.version + 1 }, true);
          }
          setConflict(null);
        },
      });
    }
    setEditing(null);
  }

  function handleCreateCorrection(values: CorrectionFormValues) {
    if (!correctionFor) return;
    addCorrection({ saleId: correctionFor.id, deltaQty: values.deltaQty, reason: values.reason, createdAt: new Date().toISOString() });
    setCorrectionFor(null);
  }

  function handleSubmit(values: SaleFormValues) {
    addSale(values);
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-[2fr,1fr]">
        <div className="space-y-4">
          <KpiCards items={kpiItems} />
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-700">Мои продажи</h2>
              <SyncControl variant="inline" />
            </div>
            <p className="mt-2 text-sm text-slate-500">Редактируйте продажи до закрытия периода. Для закрытых записей доступна коррекция.</p>
            <div className="mt-4 space-y-4">
              <ResponsiveTable data={sales} columns={[...columns, { key: "id", label: "Действия", render: (item) => (
                <div className="flex flex-wrap gap-2 text-xs">
                  {item.status !== "locked" ? (
                    <button
                      onClick={() => setEditing(item)}
                      className="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1 text-slate-600"
                    >
                      <Pencil size={12} /> Редактировать
                    </button>
                  ) : (
                    <button
                      onClick={() => setCorrectionFor(item)}
                      className="inline-flex items-center gap-1 rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-rose-600"
                    >
                      <FileWarning size={12} /> Коррекция
                    </button>
                  )}
                  <button
                    onClick={() => deleteSale(item.id)}
                    className="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1 text-slate-400"
                  >
                    <Trash2 size={12} /> Удалить
                  </button>
                </div>
              ) }]} />
            </div>
          </div>
        </div>
        <div className="space-y-4">
          <SalesForm products={products} stores={stores} onSubmit={handleSubmit} />
          {editing && <SalesInlineEdit sale={editing} onSave={handleEditSubmit} />}
          {correctionFor && <CorrectionForm onSubmit={handleCreateCorrection} />}
          {corrections.length > 0 && (
            <div className="rounded-3xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
              <div className="text-xs font-semibold uppercase">Последние коррекции</div>
              <ul className="mt-2 space-y-1">
                {corrections.slice(0, 3).map((item) => (
                  <li key={`${item.saleId}-${item.createdAt}`}>{item.reason} · Δ{item.deltaQty}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
      <ConflictDialog
        open={Boolean(conflict)}
        title="Конфликт версий"
        payload={conflict}
        render={(item) => (
          <div className="space-y-1 text-sm text-slate-600">
            <div>Модель: {item.skuName}</div>
            <div>Количество: {item.qty}</div>
            <div>Версия: {item.version}</div>
          </div>
        )}
      />
    </div>
  );
}
